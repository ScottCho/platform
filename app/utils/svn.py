import svn.remote
from svn.exception import SvnException

from app import socketio


def diff_summary_files(svn_source_dir, start_version, end_version):
    '''
    目的：得到版本之间修改和增加的文件，不包括目录
    输入参数：源码的SVN地址，
    source_file_list=[{'path': 'https://xxx/xxx.java','item': 'modified','kind': 'file'},
                        {'path': 'https://xxx/xxx.gif','item': 'added','kind': 'file'}]  
    '''

    remote = svn.remote.RemoteClient(svn_source_dir)
    source_file_list = remote.diff_summary(start_version, end_version)
    # 转换成编译后的路径,只增加修改和增加的路径,不包括目录
    source_files = [
        f.get('path') for f in source_file_list if f.get('item') == 'modified'
        or f.get('item') == 'added' and f.get('kind') == 'file'
    ]
    return source_files


@socketio.on('baseline', namespace='/task')
def version_merge(workspace, svn_source, version, room):
    '''
    合并更新包里面的应用版本到SVN
    '''
    message = f'Merged revision {version} from {svn_source}\n'
    print(message)
    socketio.emit('baseline', message, namespace='/task', room=room)
    socketio.sleep(5)
    # 更新SVN中的Jenkins中的源码目录
    try:
        workcopy = svn.local.LocalClient(workspace)
        workcopy.update()
        source_log = workcopy.run_command('log', [svn_source, '-c', version])
        commit_log = '\n'.join(source_log[3:5])
        print(commit_log)
        merge_result = workcopy.run_command('merge', [svn_source, workspace, '-c', version])
        if len(merge_result) > 2 and 'conflicts' in merge_result[3]:
            merge_msg = '合并' + version + '出现冲突,还原至合并之前\n'
            print(merge_msg)
            socketio.emit('baseline', merge_msg, namespace='/task', room=room)
            workcopy.run_command('revert', ['-R', workspace])
        else:
            # 提交
            workcopy.commit(message)
            merge_msg = f'提交版本{version}\n'
            print(merge_msg)
            socketio.emit('baseline', merge_msg, namespace='/task', room=room)
    except OSError:
        socketio.emit('baseline', '不存在工作目录', namespace='/task', room=room)
    except SvnException:
        socketio.emit('baseline', 'SVN 工作目录更新异常\n', namespace='/task', room=room)
    except Exception as e:
        print(e)
        merge_msg = '合并出现错误，请检查\n'
        print(merge_msg)
        socketio.emit('baseline', merge_msg, namespace='/task', room=room)
        workcopy.run_command('revert', ['-R', workspace])
