(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d0d36a1"],{"5d51":function(t,n,e){"use strict";e.r(n),e.d(n,"fetchOptions",(function(){return s})),e.d(n,"fetchIncludedOptions",(function(){return h})),e.d(n,"fetchSubmit",(function(){return p})),e.d(n,"fetchDetail",(function(){return b})),e.d(n,"fetchSearch",(function(){return m})),e.d(n,"fetchSearchRelease",(function(){return g})),e.d(n,"fetchMerge",(function(){return O})),e.d(n,"fetchRelease",(function(){return v})),e.d(n,"fetchDeploy",(function(){return j})),e.d(n,"fetchOperation",(function(){return w})),e.d(n,"fetchAdd",(function(){return y})),e.d(n,"fetchUpdate",(function(){return D})),e.d(n,"fetchDelete",(function(){return k})),e.d(n,"updateData",(function(){return E})),e.d(n,"getRelated",(function(){return R}));e("28a5");var r=e("66f7"),c=e("f121"),o=c["a"].relationship;function a(t){var n=[];for(var e in t){var r=o[e];r&&r.alias&&n.push(r.alias)}return n}function u(t){var n=a(t),e={};for(var r in t)-1===n.indexOf(r)&&(e[r]=t[r]);return e}var i=function(t){t=u(t);var n=[];for(var e in t)"tbl"!=e&&""!=t[e]&&(/.*?id$/.test(e)?n.push('{"name":"'.concat(e,'","op":"eq","val":"').concat(t[e],'"}')):n.push('{"name":"'.concat(e,'","op":"ilike","val":"%25').concat(t[e],'%25"}')));return"filter=[".concat(n,"]")},d=function(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:1;return"page[number]=".concat(t)},f=function(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:10;return"page[size]=".concat(t)};function l(t){return c["a"].api&&c["a"].api[t]?c["a"].api[t].type:t.substring(0,t.length-1)}function s(t,n,e){return Object(r["a"])({url:"/roles?".concat(d(n),"&").concat(f(e),"&").concat(i(t)),method:"get"})}function h(t,n){return Object(r["a"])({url:"/roles/".concat(t,"?include=").concat(n),method:"get"})}function p(t){return Object(r["a"])({url:"/roles/submit_roles",method:"post",data:t})}function b(t){return Object(r["a"])({url:"/roles?".concat(i(t)),method:"get"})}function m(t,n,e){return Object(r["a"])({url:"/roles?".concat(d(n),"&").concat(f(e),"&").concat(i(t)),method:"get"})}function g(t,n,e){return Object(r["a"])({url:"/roles?".concat(d(n),"&").concat(f(e),"&").concat(i(t)),method:"get"})}function O(t){return Object(r["a"])({url:"/roles/merge/".concat(t),method:"get"})}function v(t){return Object(r["a"])({url:"/roles/release/".concat(t),method:"get"})}function j(t){return Object(r["a"])({url:"/roles/deploy/".concat(t),method:"get"})}function w(t,n){return Object(r["a"])({url:"/roles/".concat(t,"/").concat(n),method:"get"})}function y(t){var n=u(t);return Object(r["a"])({url:"/roles",method:"post",data:{data:{type:l("roles"),attributes:n}}})}function D(t){var n=u(t);return Object(r["a"])({url:"/roles/".concat(t.id),method:"patch",data:{data:{id:t.id,type:l("roles"),attributes:n}}})}function k(t){return Object(r["a"])({url:"/roles/[".concat(t,"]"),method:"DELETE"})}function E(t,n,e){return Object(r["a"])({url:"roles/".concat(e,"/relationships/projects"),method:n,data:t})}function R(t,n){return Object(r["a"])({url:"roles/".concat(t,"/relationships/").concat(n),method:"get"})}}}]);