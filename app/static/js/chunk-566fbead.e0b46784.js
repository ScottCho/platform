(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-566fbead"],{"14a5":function(e,s,t){},"58e5":function(e,s,t){"use strict";t.r(s);var r=function(){var e=this,s=e.$createElement,r=e._self._c||s;return r("div",{staticClass:"login-container"},[r("img",{staticClass:"brand-main",attrs:{src:t("d939"),alt:"Devops"}}),e._v(" "),r("el-form",{ref:"registForm",staticClass:"login-form",attrs:{model:e.registForm,rules:e.loginRules,"auto-complete":"on","label-position":"left"}},[r("div",{staticClass:"title-container"},[r("h3",{staticClass:"title"},[e._v("注册 Regist")])]),e._v(" "),r("el-form-item",{attrs:{prop:"username"}},[r("span",{staticClass:"svg-container"},[r("svg-icon",{attrs:{"icon-class":"user"}})],1),e._v(" "),r("el-input",{ref:"username",attrs:{placeholder:"真实中文名",name:"username",type:"text",tabindex:"1"},model:{value:e.registForm.username,callback:function(s){e.$set(e.registForm,"username",s)},expression:"registForm.username"}})],1),e._v(" "),r("el-form-item",{attrs:{prop:"email"}},[r("span",{staticClass:"svg-container"},[r("svg-icon",{attrs:{"icon-class":"icon-email"}})],1),e._v(" "),r("el-input",{ref:"email",attrs:{placeholder:"Email",name:"email",type:"text",tabindex:"1"},model:{value:e.registForm.email,callback:function(s){e.$set(e.registForm,"email",s)},expression:"registForm.email"}})],1),e._v(" "),r("el-form-item",{attrs:{prop:"password"}},[r("span",{staticClass:"svg-container"},[r("svg-icon",{attrs:{"icon-class":"icon-psw"}})],1),e._v(" "),r("el-input",{key:e.passwordType,ref:"password",attrs:{type:e.passwordType,placeholder:"Password",name:"password",tabindex:"2"},nativeOn:{keyup:function(s){return!s.type.indexOf("key")&&e._k(s.keyCode,"enter",13,s.key,"Enter")?null:e.handleRegist(s)}},model:{value:e.registForm.password,callback:function(s){e.$set(e.registForm,"password",s)},expression:"registForm.password"}}),e._v(" "),r("span",{staticClass:"show-pwd",on:{click:e.showPwd}},[r("svg-icon",{attrs:{"icon-class":"password"===e.passwordType?"eye":"eye-open"}})],1)],1),e._v(" "),r("el-form-item",{attrs:{prop:"password2"}},[r("span",{staticClass:"svg-container"},[r("svg-icon",{attrs:{"icon-class":"icon-psw"}})],1),e._v(" "),r("el-input",{key:e.passwordType,ref:"password2",attrs:{type:e.passwordType,placeholder:"Repeat password",name:"password",tabindex:"2"},nativeOn:{keyup:function(s){return!s.type.indexOf("key")&&e._k(s.keyCode,"enter",13,s.key,"Enter")?null:e.handleRegist(s)}},model:{value:e.registForm.password2,callback:function(s){e.$set(e.registForm,"password2",s)},expression:"registForm.password2"}}),e._v(" "),r("span",{staticClass:"show-pwd",on:{click:e.showPwd}},[r("svg-icon",{attrs:{"icon-class":"password"===e.passwordType?"eye":"eye-open"}})],1)],1),e._v(" "),r("el-form-item",{attrs:{prop:"role_id"}},[r("span",{staticClass:"svg-container"},[r("svg-icon",{attrs:{"icon-class":"peoples"}})],1),e._v(" "),r("el-select",{staticStyle:{width:"85%"},attrs:{placeholder:"请选择"},model:{value:e.registForm.role_id,callback:function(s){e.$set(e.registForm,"role_id",s)},expression:"registForm.role_id"}},e._l(e.roles,(function(e){return r("el-option",{key:e.value,attrs:{label:e.label,value:e.value}})})),1)],1),e._v(" "),r("el-button",{staticStyle:{width:"100%","margin-bottom":"30px","border-radius":"100px"},attrs:{loading:e.loading,type:"primary"},nativeOn:{click:function(s){return s.preventDefault(),e.handleRegist(s)}}},[e._v("Regist")]),e._v(" "),r("div",{staticClass:"tips"},[r("span",{on:{click:e.handleLogin}},[e._v("返回登录界面")])])],1)],1)},a=[],o=t("61f7"),i=t("c24f"),n=t("5c96"),l={name:"Login",data:function(){var e=this,s=function(e,s,t){Object(o["b"])(s)?t():t(new Error("Please enter the correct user name"))},t=function(e,s,t){s.length<6?t(new Error("The password can not be less than 6 digits")):t()},r=function(s,t,r){e.registForm.password==e.registForm.password2?r():r(new Error("the repeat password not equal"))};return{registForm:{username:"",password:"",password2:"",email:"",role_id:"1"},roles:[{value:"1",label:"developer"},{value:"2",label:"Tester"},{value:"3",label:"Moderator"}],loginRules:{username:[{required:!0,trigger:"blur",validator:s}],password:[{required:!0,trigger:"blur",validator:t}],password2:[{required:!0,trigger:"blur",validator:r}]},loading:!1,passwordType:"password",redirect:void 0}},watch:{$route:{handler:function(e){this.redirect=e.query&&e.query.redirect},immediate:!0}},methods:{handleRegist:function(){var e=this;this.$refs.registForm.validate((function(s){s&&Object(i["regist"])(e.registForm).then((function(s){s&&n["MessageBox"].confirm("注册成功，请在邮箱中激活账户。\n"+e.registForm.email,"注册成功",{confirmButtonText:"返回登录",cancelButtonText:"Cancel",type:"info"}).then((function(){e.handleLogin()}))})).catch((function(e){console.log(e)}))}))},showPwd:function(){var e=this;"password"===this.passwordType?this.passwordType="":this.passwordType="password",this.$nextTick((function(){e.$refs.password.focus()}))},handleLogin:function(){this.$router.push({path:"/login"})}}},c=l,p=(t("88ba"),t("ba6e"),t("2877")),d=Object(p["a"])(c,r,a,!1,null,"bcefc8ca",null);s["default"]=d.exports},"88ba":function(e,s,t){"use strict";var r=t("14a5"),a=t.n(r);a.a},ba6e:function(e,s,t){"use strict";var r=t("c9b6"),a=t.n(r);a.a},c9b6:function(e,s,t){},d939:function(e,s,t){e.exports=t.p+"static/img/logo-white.5cd6a03e.png"}}]);