(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-b461012a"],{ad8f:function(e,r,t){"use strict";t.r(r),t.d(r,"getList",(function(){return o}));var n=t("b775");function o(e){return Object(n["a"])({url:"/table/list",method:"get",params:e})}},b775:function(e,r,t){"use strict";var n=t("bc3a"),o=t.n(n),s=t("5c96"),a=t("4360"),c=t("5f87"),i=o.a.create({baseURL:"/api",timeout:5e3});i.interceptors.request.use((function(e){return a["a"].getters.token&&(e.headers["X-Token"]=Object(c["a"])()),e}),(function(e){return console.log(e),Promise.reject(e)})),i.interceptors.response.use((function(e){var r=e.data;return"0000"!==r.resCode?(Object(s["Message"])({message:r.message||"Error",type:"error",duration:5e3}),50008!==r.resCode&&50012!==r.resCode&&50014!==r.resCode||s["MessageBox"].confirm("You have been logged out, you can cancel to stay on this page, or log in again","Confirm logout",{confirmButtonText:"Re-Login",cancelButtonText:"Cancel",type:"warning"}).then((function(){a["a"].dispatch("user/resetToken").then((function(){location.reload()}))})),Promise.reject(new Error(r.message||"Error"))):r}),(function(e){return console.log("err"+e),Object(s["Message"])({message:e.message,type:"error",duration:5e3}),Promise.reject(e)})),r["a"]=i}}]);