(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d0b2c5b"],{2612:function(t,e,n){"use strict";n.r(e),n.d(e,"fetchOptions",(function(){return u})),n.d(e,"fetchSubmit",(function(){return c})),n.d(e,"fetchFind",(function(){return a})),n.d(e,"fetchSearch",(function(){return o})),n.d(e,"fetchSearchRelease",(function(){return s})),n.d(e,"fetchAdd",(function(){return i})),n.d(e,"fetchUpdate",(function(){return f})),n.d(e,"fetchDelete",(function(){return h}));var r=n("b775");function u(t){return Object(r["a"])({url:"/users/options",method:"get",params:t})}function c(t){return Object(r["a"])({url:"/users/submit_users",method:"post",data:t})}function a(t){if("string"==typeof t)return Object(r["a"])({url:"/users/find/".concat(t),method:"get"});var e=[],n=[];for(var u in t)"tbl"!=u&&(e.push(u+"="+t[u]),n.push(t[u]));var c=e.length;return 1==c?Object(r["a"])({url:"/users/find/".concat(n[0]),method:"get"}):c>1?Object(r["a"])({url:"/users/find?".concat(e.join("&")),method:"get"}):void 0}function o(t,e,n){return Object(r["a"])({url:"/users?page[number]=".concat(e,"&page[size]=").concat(n),method:"get"})}function s(t,e,n){return Object(r["a"])({url:"/users/release_search?_pageNo=".concat(e-1,"&_pageSize=").concat(n),method:"post",data:t})}function i(t){return Object(r["a"])({url:"/users",method:"post",data:{data:{type:d("users"),attributes:t}}})}function d(t){return t.substring(0,t.length-1)}function f(t){return Object(r["a"])({url:"/users/".concat(t.id),method:"patch",data:{data:{id:t.id,type:d("users"),attributes:t}}})}function h(t){return Object(r["a"])({url:"/users/".concat(t),method:"DELETE"})}}}]);