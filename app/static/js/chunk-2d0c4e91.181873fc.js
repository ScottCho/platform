(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d0c4e91"],{"3d9c":function(e,t,n){"use strict";n.r(t),n.d(t,"fetchOptions",(function(){return r})),n.d(t,"fetchSubmit",(function(){return u})),n.d(t,"fetchFind",(function(){return a})),n.d(t,"fetchSearch",(function(){return d})),n.d(t,"fetchSearchRelease",(function(){return o})),n.d(t,"fetchAdd",(function(){return i})),n.d(t,"fetchUpdate",(function(){return f})),n.d(t,"fetchDelete",(function(){return h}));var c=n("b775");function r(e){return Object(c["a"])({url:"/credences/options",method:"get",params:e})}function u(e){return Object(c["a"])({url:"/credences/submit_credences",method:"post",data:e})}function a(e){if("string"==typeof e)return Object(c["a"])({url:"/credences/find/".concat(e),method:"get"});var t=[],n=[];for(var r in e)"tbl"!=r&&(t.push(r+"="+e[r]),n.push(e[r]));var u=t.length;return 1==u?Object(c["a"])({url:"/credences/find/".concat(n[0]),method:"get"}):u>1?Object(c["a"])({url:"/credences/find?".concat(t.join("&")),method:"get"}):void 0}function d(e,t,n){return Object(c["a"])({url:"/credences?page[number]=".concat(t,"&page[size]=").concat(n),method:"get"})}function o(e,t,n){return Object(c["a"])({url:"/credences/release_search?_pageNo=".concat(t-1,"&_pageSize=").concat(n),method:"post",data:e})}function i(e){return Object(c["a"])({url:"/credences",method:"post",data:{data:{type:s("credences"),attributes:e}}})}function s(e){return e.substring(0,e.length-1)}function f(e){return Object(c["a"])({url:"/credences/".concat(e.id),method:"patch",data:{data:{id:e.id,type:s("credences"),attributes:e}}})}function h(e){return Object(c["a"])({url:"/credences/".concat(e),method:"DELETE"})}}}]);