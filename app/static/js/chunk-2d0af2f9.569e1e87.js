(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d0af2f9"],{"0cf6":function(t,e,n){"use strict";n.r(e),n.d(e,"fetchOptions",(function(){return c})),n.d(e,"fetchSubmit",(function(){return r})),n.d(e,"fetchFind",(function(){return u})),n.d(e,"fetchSearch",(function(){return o})),n.d(e,"fetchSearchRelease",(function(){return i})),n.d(e,"fetchAdd",(function(){return d})),n.d(e,"fetchUpdate",(function(){return f})),n.d(e,"fetchDelete",(function(){return p}));var a=n("b775");function c(t){return Object(a["a"])({url:"/packages/options",method:"get",params:t})}function r(t){return Object(a["a"])({url:"/packages/submit_packages",method:"post",data:t})}function u(t){if("string"==typeof t)return Object(a["a"])({url:"/packages/find/".concat(t),method:"get"});var e=[],n=[];for(var c in t)"tbl"!=c&&(e.push(c+"="+t[c]),n.push(t[c]));var r=e.length;return 1==r?Object(a["a"])({url:"/packages/find/".concat(n[0]),method:"get"}):r>1?Object(a["a"])({url:"/packages/find?".concat(e.join("&")),method:"get"}):void 0}function o(t,e,n){return Object(a["a"])({url:"/packages?page[number]=".concat(e,"&page[size]=").concat(n),method:"get"})}function i(t,e,n){return Object(a["a"])({url:"/packages/release_search?_pageNo=".concat(e-1,"&_pageSize=").concat(n),method:"post",data:t})}function d(t){return Object(a["a"])({url:"/packages",method:"post",data:{data:{type:s("packages"),attributes:t}}})}function s(t){return t.substring(0,t.length-1)}function f(t){return Object(a["a"])({url:"/packages/".concat(t.id),method:"patch",data:{data:{id:t.id,type:s("packages"),attributes:t}}})}function p(t){return Object(a["a"])({url:"/packages/".concat(t),method:"DELETE"})}}}]);