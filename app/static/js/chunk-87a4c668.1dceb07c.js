(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-87a4c668"],{2017:function(e,n,s){"use strict";var o=s("b12d"),t=s.n(o);t.a},"241d":function(e,n,s){},3722:function(e,n,s){"use strict";var o=s("241d"),t=s.n(o);t.a},"9ed6":function(e,n,s){"use strict";s.r(n);var o=function(){var e=this,n=e.$createElement,s=e._self._c||n;return s("div",{staticClass:"login-container"},[s("el-form",{ref:"loginForm",staticClass:"login-form",attrs:{model:e.loginForm,rules:e.loginRules,"auto-complete":"on","label-position":"left"}},[s("div",{staticClass:"title-container"},[s("h3",{staticClass:"title"},[e._v("Login Form")])]),e._v(" "),s("el-form-item",{attrs:{prop:"username"}},[s("span",{staticClass:"svg-container"},[s("svg-icon",{attrs:{"icon-class":"user"}})],1),e._v(" "),s("el-input",{ref:"username",attrs:{placeholder:"Username",name:"username",type:"text",tabindex:"1","auto-complete":"on"},model:{value:e.loginForm.username,callback:function(n){e.$set(e.loginForm,"username",n)},expression:"loginForm.username"}})],1),e._v(" "),s("el-form-item",{attrs:{prop:"password"}},[s("span",{staticClass:"svg-container"},[s("svg-icon",{attrs:{"icon-class":"password"}})],1),e._v(" "),s("el-input",{key:e.passwordType,ref:"password",attrs:{type:e.passwordType,placeholder:"Password",name:"password",tabindex:"2","auto-complete":"on"},nativeOn:{keyup:function(n){return!n.type.indexOf("key")&&e._k(n.keyCode,"enter",13,n.key,"Enter")?null:e.handleLogin(n)}},model:{value:e.loginForm.password,callback:function(n){e.$set(e.loginForm,"password",n)},expression:"loginForm.password"}}),e._v(" "),s("span",{staticClass:"show-pwd",on:{click:e.showPwd}},[s("svg-icon",{attrs:{"icon-class":"password"===e.passwordType?"eye":"eye-open"}})],1)],1),e._v(" "),s("el-button",{staticStyle:{width:"100%","margin-bottom":"30px"},attrs:{loading:e.loading,type:"primary"},nativeOn:{click:function(n){return n.preventDefault(),e.handleLogin(n)}}},[e._v("Login")]),e._v(" "),s("div",{staticClass:"tips"},[s("span",{staticStyle:{"margin-right":"20px"}},[e._v("username: admin")]),e._v(" "),s("span",[e._v("password: any")])])],1)],1)},t=[],r=s("61f7"),a={name:"Login",data:function(){var e=function(e,n,s){Object(r["b"])(n)?s():s(new Error("Please enter the correct user name"))},n=function(e,n,s){n.length<6?s(new Error("The password can not be less than 6 digits")):s()};return{loginForm:{username:"admin",password:"111111"},loginRules:{username:[{required:!0,trigger:"blur",validator:e}],password:[{required:!0,trigger:"blur",validator:n}]},loading:!1,passwordType:"password",redirect:void 0}},watch:{$route:{handler:function(e){this.redirect=e.query&&e.query.redirect},immediate:!0}},methods:{showPwd:function(){var e=this;"password"===this.passwordType?this.passwordType="":this.passwordType="password",this.$nextTick((function(){e.$refs.password.focus()}))},handleLogin:function(){var e=this;this.$refs.loginForm.validate((function(n){if(!n)return console.log("error submit!!"),!1;e.loading=!0,e.$store.dispatch("user/login",e.loginForm).then((function(){console.log("login ok"),e.$router.push({path:"/"}),e.loading=!1})).catch((function(){console.log("login error"),e.loading=!1}))}))}}},i=a,l=(s("2017"),s("3722"),s("2877")),c=Object(l["a"])(i,o,t,!1,null,"984cd87e",null);n["default"]=c.exports},b12d:function(e,n,s){}}]);