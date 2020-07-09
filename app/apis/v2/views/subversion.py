from app.apis.v2 import api_v2
from app.apis.v2.auth import auth_required
from app.models.service import App
from flask import request
from app.apis.v2.message import success_msg, api_abort
import svn.remote


@api_v2.route('/repo/svn/<int:app_id>/')
@api_v2.route('/repo/svn/<int:app_id>/<path:subpath>')
# @auth_required
def repo(app_id, subpath=None):
    '''
    tab为操作类型：None:文件列表，history:文件历史, files:文件查看, compare:文件比较
    '''
    try:
        app = App.query.get(app_id)
        sourcecode = app.source_dir
        # repo_url = f'{sourcecode}/{subpath}' if subpath else app.source_dir
        remote = svn.remote.RemoteClient(sourcecode)
        tab = request.args.get('tab')
        response = ''
        if tab is None:
            entries = remote.list(extended=True, rel_path=subpath)
            response = success_msg(status=200,
                                   data=[entry for entry in entries])
        elif tab == 'history':
            entries = remote.log_default(rel_filepath=subpath)
            response = success_msg(status=200,
                                   data=[entry for entry in entries])
        elif tab == 'files':
            entries = remote.cat(subpath)
            response = success_msg(status=200, data=entries.decode('GBK'))
        elif tab == 'compare':
            old = request.args.get('old')
            new = request.args.get('new')
            old_txt = remote.cat(subpath, old)
            new_txt = remote.cat(subpath, new)
            entries = {
                'oldStr': old_txt.decode('GBK'),
                'newStr': new_txt.decode('GBK')
            }
    except UnicodeError as e:
        return api_abort(status=10011, detail=str(e), source='subversion')
    except Exception as e:
        return api_abort(status=10000, detail=str(e), source='subversion')
    else:
        return response
