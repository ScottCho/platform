(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d0b2736"],{"23ba":function(t,e,n){"use strict";n.r(e),n.d(e,"fetchOptions",(function(){return u})),n.d(e,"fetchSubmit",(function(){return o})),n.d(e,"fetchFind",(function(){return c})),n.d(e,"fetchSearch",(function(){return a})),n.d(e,"fetchSearchRelease",(function(){return i})),n.d(e,"fetchAdd",(function(){return d})),n.d(e,"fetchUpdate",(function(){return f})),n.d(e,"fetchDelete",(function(){return h}));var r=n("b775");function u(t){return Object(r["a"])({url:"/group/options",method:"get",params:t})}function o(t){return Object(r["a"])({url:"/group/submit_group",method:"post",data:t})}function c(t){if("string"==typeof t)return Object(r["a"])({url:"/group/find/".concat(t),method:"get"});var e=[],n=[];for(var u in t)"tbl"!=u&&(e.push(u+"="+t[u]),n.push(t[u]));var o=e.length;return 1==o?Object(r["a"])({url:"/group/find/".concat(n[0]),method:"get"}):o>1?Object(r["a"])({url:"/group/find?".concat(e.join("&")),method:"get"}):void 0}function a(t,e,n){return Object(r["a"])({url:"/group?page[number]=".concat(e,"&page[size]=").concat(n),method:"get"})}function i(t,e,n){return Object(r["a"])({url:"/group/release_search?_pageNo=".concat(e-1,"&_pageSize=").concat(n),method:"post",data:t})}function d(t){return Object(r["a"])({url:"/group",method:"post",data:{data:{type:p("group"),attributes:t}}})}function p(t){return t.substring(0,t.length-1)}function f(t){return Object(r["a"])({url:"/group/".concat(t.id),method:"patch",data:{data:{id:t.id,type:p("group"),attributes:t}}})}function h(t){return Object(r["a"])({url:"/group/".concat(t),method:"DELETE"})}}}]);