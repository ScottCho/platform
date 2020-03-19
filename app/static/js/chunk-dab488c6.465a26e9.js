(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-dab488c6"],{2017:function(e,o,t){"use strict";var n=t("b12d"),s=t.n(n);s.a},"2d10":function(e,o,t){"use strict";var n=t("f23d"),s=t.n(n);s.a},"9ed6":function(e,o,t){"use strict";t.r(o);var n=function(){var e=this,o=e.$createElement,t=e._self._c||o;return t("div",{staticClass:"login-container"},[t("el-form",{ref:"loginForm",staticClass:"login-form",attrs:{model:e.loginForm,rules:e.loginRules,"auto-complete":"on","label-position":"left"}},[t("div",{staticClass:"title-container"},[t("h3",{staticClass:"title"},[e._v("Login Form")])]),e._v(" "),t("el-form-item",{attrs:{prop:"username"}},[t("span",{staticClass:"svg-container"},[t("svg-icon",{attrs:{"icon-class":"email"}})],1),e._v(" "),t("el-input",{ref:"username",attrs:{placeholder:"email",name:"username",type:"text",tabindex:"1","auto-complete":"on"},model:{value:e.loginForm.username,callback:function(o){e.$set(e.loginForm,"username",o)},expression:"loginForm.username"}})],1),e._v(" "),t("el-form-item",{attrs:{prop:"password"}},[t("span",{staticClass:"svg-container"},[t("svg-icon",{attrs:{"icon-class":"password"}})],1),e._v(" "),t("el-input",{key:e.passwordType,ref:"password",attrs:{type:e.passwordType,placeholder:"Password",name:"password",tabindex:"2","auto-complete":"on"},nativeOn:{keyup:function(o){return!o.type.indexOf("key")&&e._k(o.keyCode,"enter",13,o.key,"Enter")?null:e.handleLogin(o)}},model:{value:e.loginForm.password,callback:function(o){e.$set(e.loginForm,"password",o)},expression:"loginForm.password"}}),e._v(" "),t("span",{staticClass:"show-pwd",on:{click:e.showPwd}},[t("svg-icon",{attrs:{"icon-class":"password"===e.passwordType?"eye":"eye-open"}})],1)],1),e._v(" "),t("el-button",{staticStyle:{width:"100%","margin-bottom":"30px"},attrs:{loading:e.loading,type:"primary"},nativeOn:{click:function(o){return o.preventDefault(),e.handleLogin(o)}}},[e._v("Login")]),e._v(" "),t("div",{staticClass:"tips"},[t("span",{on:{click:e.handleRegist}},[e._v(" 注册新用户")])])],1)],1)},s=[],r=t("61f7"),a={name:"Login",data:function(){var e=function(e,o,t){Object(r["b"])(o)?t():t(new Error("Please enter the correct user name"))},o=function(e,o,t){o.length<6?t(new Error("The password can not be less than 6 digits")):t()};return{loginForm:{username:"",password:""},loginRules:{username:[{required:!0,trigger:"blur",validator:e}],password:[{required:!0,trigger:"blur",validator:o}]},loading:!1,passwordType:"password",redirect:void 0}},watch:{$route:{handler:function(e){this.redirect=e.query&&e.query.redirect},immediate:!0}},methods:{handleRegist:function(){this.$router.push({path:"/regist"})},showPwd:function(){var e=this;"password"===this.passwordType?this.passwordType="":this.passwordType="password",this.$nextTick((function(){e.$refs.password.focus()}))},handleLogin:function(){var e=this;this.$refs.loginForm.validate((function(o){if(!o)return console.log("error submit!!"),!1;e.loading=!0,e.$store.dispatch("user/login",e.loginForm).then((function(){console.log("login ok"),e.$router.push({path:"/"}),e.loading=!1})).catch((function(){console.log("login error"),e.loading=!1}))}))}}},i=a,l=(t("2017"),t("2d10"),t("2877")),c=Object(l["a"])(i,n,s,!1,null,"23c21dfc",null);o["default"]=c.exports},b12d:function(e,o,t){},f23d:function(e,o,t){}}]);