(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d0a3128"],{"012c":function(e,o,n){"use strict";n.r(o);var r=n("bc3a"),t=n.n(r),s=n("5c96"),a=n("4360"),c=n("5f87"),i=t.a.create({baseURL:"/zhaoyong-api",timeout:5e3});i.interceptors.request.use((function(e){return a["a"].getters.token&&(e.headers["X-Token"]=Object(c["a"])()),e}),(function(e){return console.log(e),Promise.reject(e)})),i.interceptors.response.use((function(e){var o=e.data;return o?"0000"!==o.resCode?(Object(s["Message"])({message:o.message||"Error",type:"error",duration:5e3}),50008!==o.resCode&&50012!==o.resCode&&50014!==o.resCode||s["MessageBox"].confirm("You have been logged out, you can cancel to stay on this page, or log in again","Confirm logout",{confirmButtonText:"Re-Login",cancelButtonText:"Cancel",type:"warning"}).then((function(){a["a"].dispatch("user/resetToken").then((function(){location.reload()}))})),Promise.reject(new Error(o.message||"Error"))):o:(console.log(e),{resCode:"0000",resData:null,resMsg:"成功"})}),(function(e){return console.log("err"+e),Object(s["Message"])({message:e.message,type:"error",duration:5e3}),Promise.reject(e)}));var u=i;function g(e,o,n){return u({url:"gg_code/find_business_list_page_by_code?_pageNo=".concat(o-1,"&_pageSize=").concat(n),method:"post",data:e})}n.d(o,"fetchOptions",(function(){return g}))}}]);