from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from subprocess import Popen, PIPE

from csc2518.settings import RELATIVE_STATIC_URL
from datacollector.models import *
website_hostname = Settings.objects.get(setting_name="website_hostname").setting_value
website_name = Settings.objects.get(setting_name="website_name").setting_value

# Global variables for HTML emails
global emailPre, emailPost
emailPre = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html><head>
    <title></title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <style type="text/css">
body {
  margin: 0;
  mso-line-height-rule: exactly;
  padding: 0;
  min-width: 100%;
}
table {
  border-collapse: collapse;
  border-spacing: 0;
}
td {
  padding: 0;
  vertical-align: top;
}
.spacer,
.border {
  font-size: 1px;
  line-height: 1px;
}
.spacer {
  width: 100%;
}
img {
  border: 0;
  -ms-interpolation-mode: bicubic;
}
.image {
  font-size: 12px;
  Margin-bottom: 24px;
  mso-line-height-rule: at-least;
}
.image img {
  display: block;
}
.logo {
  mso-line-height-rule: at-least;
}
.logo img {
  display: block;
}
strong {
  font-weight: bold;
}
h1,
h2,
h3,
p,
ol,
ul,
li {
  Margin-top: 0;
}
ol,
ul,
li {
  padding-left: 0;
}
blockquote {
  Margin-top: 0;
  Margin-right: 0;
  Margin-bottom: 0;
  padding-right: 0;
}
.column-top {
  font-size: 50px;
  line-height: 50px;
}
.column-bottom {
  font-size: 26px;
  line-height: 26px;
}
.column {
  text-align: left;
}
.contents {
  table-layout: fixed;
  width: 100%;
  Margin-top: 10;
}
.padded {
  padding-left: 50px;
  padding-right: 50px;
  word-break: break-word;
  word-wrap: break-word;
}
.wrapper {
  display: table;
  table-layout: fixed;
  width: 100%;
  min-width: 620px;
  -webkit-text-size-adjust: 100%;
  -ms-text-size-adjust: 100%;
}
table.wrapper {
  table-layout: fixed;
}
.one-col,
.two-col,
.three-col {
  Margin-left: auto;
  Margin-right: auto;
  width: 600px;
}
.centered {
  Margin-left: auto;
  Margin-right: auto;
}
.two-col .image {
  Margin-bottom: 21px;
}
.two-col .column-bottom {
  font-size: 29px;
  line-height: 29px;
}
.two-col .column {
  width: 300px;
}
.two-col .first .padded {
  padding-left: 50px;
  padding-right: 25px;
}
.two-col .second .padded {
  padding-left: 25px;
  padding-right: 50px;
}
.three-col .image {
  Margin-bottom: 18px;
}
.three-col .column-bottom {
  font-size: 32px;
  line-height: 32px;
}
.three-col .column {
  width: 200px;
}
.three-col .first .padded {
  padding-left: 50px;
  padding-right: 10px;
}
.three-col .second .padded {
  padding-left: 30px;
  padding-right: 30px;
}
.three-col .third .padded {
  padding-left: 10px;
  padding-right: 50px;
}
.wider {
  width: 400px;
}
.narrower {
  width: 200px;
}
@media only screen and (min-width: 0) {
  .wrapper {
    text-rendering: optimizeLegibility;
  }
}
@media only screen and (max-width: 620px) {
  [class=wrapper] {
    min-width: 320px !important;
    width: 100% !important;
  }
  [class=wrapper] .one-col,
  [class=wrapper] .two-col,
  [class=wrapper] .three-col {
    width: 320px !important;
  }
  [class=wrapper] .column,
  [class=wrapper] .gutter {
    display: block;
    float: left;
    width: 320px !important;
  }
  [class=wrapper] .padded {
    padding-left: 20px !important;
    padding-right: 20px !important;
  }
  [class=wrapper] .block {
    display: block !important;
  }
  [class=wrapper] .hide {
    display: none !important;
  }
  [class=wrapper] .image {
    margin-bottom: 24px !important;
  }
  [class=wrapper] .image img {
    height: auto !important;
    width: 100% !important;
  }
}
.wrapper h1 {
  font-weight: 400;
}
.wrapper h2 {
  font-weight: 700;
}
.wrapper h3 {
  font-weight: 400;
}
.wrapper blockquote p,
.wrapper blockquote ol,
.wrapper blockquote ul {
  font-style: italic;
}
td.border {
  width: 1px;
}
tr.border {
  background-color: #e3e3e3;
  height: 1px;
}
tr.border td {
  line-height: 1px;
}
.sidebar {
  width: 600px;
}
.first.wider .padded {
  padding-left: 50px;
  padding-right: 30px;
}
.second.wider .padded {
  padding-left: 30px;
  padding-right: 50px;
}
.first.narrower .padded {
  padding-left: 50px;
  padding-right: 10px;
}
.second.narrower .padded {
  padding-left: 10px;
  padding-right: 50px;
}
.divider {
  Margin-bottom: 24px;
}
.wrapper h1 {
  font-size: 40px;
  Margin-bottom: 20px;
}
.wrapper h2 {
  font-size: 24px;
  Margin-bottom: 16px;
}
.wrapper h3 {
  font-size: 18px;
  Margin-bottom: 12px;
}
.wrapper a {
  text-decoration: none;
}
.wrapper a:hover {
  border-bottom: 0;
  text-decoration: none;
}
.wrapper h1 a,
.wrapper h2 a,
.wrapper h3 a {
  border: none;
}
.wrapper p,
.wrapper ol,
.wrapper ul {
  font-size: 15px;
}
.wrapper ol,
.wrapper ul {
  Margin-left: 20px;
}
.wrapper li {
  padding-left: 2px;
}
.wrapper blockquote {
  Margin: 0;
  padding-left: 18px;
}
.btn {
  Margin-bottom: 27px;
}
.btn a {
  border: 0;
  border-radius: 4px;
  display: inline-block;
  font-size: 14px;
  font-weight: 700;
  line-height: 21px;
  padding: 9px 22px 8px 22px;
  text-align: center;
  text-decoration: none;
}
.btn a:hover {
  Position: relative;
  top: 3px;
}
.one-col,
.two-col,
.three-col,
.sidebar {
  background-color: #ffffff;
  table-layout: fixed;
}
.one-col .column table:nth-last-child(2) td h1:last-child,
.one-col .column table:nth-last-child(2) td h2:last-child,
.one-col .column table:nth-last-child(2) td h3:last-child,
.one-col .column table:nth-last-child(2) td p:last-child,
.one-col .column table:nth-last-child(2) td ol:last-child,
.one-col .column table:nth-last-child(2) td ul:last-child {
  Margin-bottom: 24px;
}
.wrapper .two-col .column table:nth-last-child(2) td h1:last-child,
.wrapper .wider .column table:nth-last-child(2) td h1:last-child,
.wrapper .two-col .column table:nth-last-child(2) td h2:last-child,
.wrapper .wider .column table:nth-last-child(2) td h2:last-child,
.wrapper .two-col .column table:nth-last-child(2) td h3:last-child,
.wrapper .wider .column table:nth-last-child(2) td h3:last-child,
.wrapper .two-col .column table:nth-last-child(2) td p:last-child,
.wrapper .wider .column table:nth-last-child(2) td p:last-child,
.wrapper .two-col .column table:nth-last-child(2) td ol:last-child,
.wrapper .wider .column table:nth-last-child(2) td ol:last-child,
.wrapper .two-col .column table:nth-last-child(2) td ul:last-child,
.wrapper .wider .column table:nth-last-child(2) td ul:last-child {
  Margin-bottom: 21px;
}
.wrapper .two-col h1,
.wrapper .wider h1 {
  font-size: 28px;
  Margin-bottom: 18px;
}
.wrapper .two-col h2,
.wrapper .wider h2 {
  font-size: 20px;
  Margin-bottom: 14px;
}
.wrapper .two-col h3,
.wrapper .wider h3 {
  font-size: 17px;
  Margin-bottom: 10px;
}
.wrapper .two-col p,
.wrapper .wider p,
.wrapper .two-col ol,
.wrapper .wider ol,
.wrapper .two-col ul,
.wrapper .wider ul {
  font-size: 13px;
}
.wrapper .two-col blockquote,
.wrapper .wider blockquote {
  padding-left: 16px;
}
.wrapper .two-col .divider,
.wrapper .wider .divider {
  Margin-bottom: 21px;
}
.wrapper .two-col .btn,
.wrapper .wider .btn {
  Margin-bottom: 24px;
}
.wrapper .two-col .btn a,
.wrapper .wider .btn a {
  font-size: 12px;
  line-height: 19px;
  padding: 6px 17px 6px 17px;
}
.wrapper .three-col .column table:nth-last-child(2) td h1:last-child,
.wrapper .narrower .column table:nth-last-child(2) td h1:last-child,
.wrapper .three-col .column table:nth-last-child(2) td h2:last-child,
.wrapper .narrower .column table:nth-last-child(2) td h2:last-child,
.wrapper .three-col .column table:nth-last-child(2) td h3:last-child,
.wrapper .narrower .column table:nth-last-child(2) td h3:last-child,
.wrapper .three-col .column table:nth-last-child(2) td p:last-child,
.wrapper .narrower .column table:nth-last-child(2) td p:last-child,
.wrapper .three-col .column table:nth-last-child(2) td ol:last-child,
.wrapper .narrower .column table:nth-last-child(2) td ol:last-child,
.wrapper .three-col .column table:nth-last-child(2) td ul:last-child,
.wrapper .narrower .column table:nth-last-child(2) td ul:last-child {
  Margin-bottom: 18px;
}
.wrapper .three-col h1,
.wrapper .narrower h1 {
  font-size: 24px;
  Margin-bottom: 16px;
}
.wrapper .three-col h2,
.wrapper .narrower h2 {
  font-size: 18px;
  Margin-bottom: 12px;
}
.wrapper .three-col h3,
.wrapper .narrower h3 {
  font-size: 15px;
  Margin-bottom: 8px;
}
.wrapper .three-col p,
.wrapper .narrower p,
.wrapper .three-col ol,
.wrapper .narrower ol,
.wrapper .three-col ul,
.wrapper .narrower ul {
  font-size: 12px;
}
.wrapper .three-col ol,
.wrapper .narrower ol,
.wrapper .three-col ul,
.wrapper .narrower ul {
  Margin-left: 14px;
}
.wrapper .three-col li,
.wrapper .narrower li {
  padding-left: 1px;
}
.wrapper .three-col blockquote,
.wrapper .narrower blockquote {
  padding-left: 12px;
}
.wrapper .three-col .divider,
.wrapper .narrower .divider {
  Margin-bottom: 18px;
}
.wrapper .three-col .btn,
.wrapper .narrower .btn {
  Margin-bottom: 21px;
}
.wrapper .three-col .btn a,
.wrapper .narrower .btn a {
  font-size: 10px;
  line-height: 16px;
  padding: 5px 17px 5px 17px;
}
.wrapper .wider .column-bottom {
  font-size: 29px;
  line-height: 29px;
}
.wrapper .wider .image {
  Margin-bottom: 21px;
}
.wrapper .narrower .column-bottom {
  font-size: 32px;
  line-height: 32px;
}
.wrapper .narrower .image {
  Margin-bottom: 18px;
}
.header {
  Margin-left: auto;
  Margin-right: auto;
  width: 600px;
}
.header .logo {
  padding-bottom: 40px;
  padding-top: 40px;
  width: 280px;
}
.header .logo div {
  font-size: 24px;
  font-weight: 700;
  line-height: 30px;
}
.header .logo div a {
  text-decoration: none;
}
.header .logo div.logo-center {
  text-align: center;
}
.header .logo div.logo-center img {
  Margin-left: auto;
  Margin-right: auto;
}
.header .preheader {
  padding-bottom: 40px;
  padding-top: 40px;
  text-align: right;
  width: 280px;
}
.preheader,
.footer {
  letter-spacing: 0.01em;
  font-style: normal;
  line-height: 17px;
  font-weight: 400;
}
.preheader a,
.footer a {
  letter-spacing: 0.03em;
  font-style: normal;
  font-weight: 700;
}
.preheader,
.footer,
.footer .social a {
  font-size: 11px;
}
.footer {
  Margin-right: auto;
  Margin-left: auto;
  padding-top: 50px;
  padding-bottom: 40px;
  width: 602px;
}
.footer table {
  Margin-left: auto;
  Margin-right: auto;
}
.footer .social {
  text-transform: uppercase;
}
.footer .social span {
  mso-text-raise: 4px;
}
.footer .social td {
  padding-bottom: 30px;
  padding-left: 20px;
  padding-right: 20px;
}
.footer .social a {
  display: block;
  transition: opacity 0.2s;
}
.footer .social a:hover {
  opacity: 0.75;
}
.footer .address {
  Margin-bottom: 19px;
}
.footer .permission {
  Margin-bottom: 10px;
}
@media only screen and (max-width: 620px) {
  [class=wrapper] .one-col .column:last-child table:nth-last-child(2) td h1:last-child,
  [class=wrapper] .two-col .column:last-child table:nth-last-child(2) td h1:last-child,
  [class=wrapper] .three-col .column:last-child table:nth-last-child(2) td h1:last-child,
  [class=wrapper] .one-col .column:last-child table:nth-last-child(2) td h2:last-child,
  [class=wrapper] .two-col .column:last-child table:nth-last-child(2) td h2:last-child,
  [class=wrapper] .three-col .column:last-child table:nth-last-child(2) td h2:last-child,
  [class=wrapper] .one-col .column:last-child table:nth-last-child(2) td h3:last-child,
  [class=wrapper] .two-col .column:last-child table:nth-last-child(2) td h3:last-child,
  [class=wrapper] .three-col .column:last-child table:nth-last-child(2) td h3:last-child,
  [class=wrapper] .one-col .column:last-child table:nth-last-child(2) td p:last-child,
  [class=wrapper] .two-col .column:last-child table:nth-last-child(2) td p:last-child,
  [class=wrapper] .three-col .column:last-child table:nth-last-child(2) td p:last-child,
  [class=wrapper] .one-col .column:last-child table:nth-last-child(2) td ol:last-child,
  [class=wrapper] .two-col .column:last-child table:nth-last-child(2) td ol:last-child,
  [class=wrapper] .three-col .column:last-child table:nth-last-child(2) td ol:last-child,
  [class=wrapper] .one-col .column:last-child table:nth-last-child(2) td ul:last-child,
  [class=wrapper] .two-col .column:last-child table:nth-last-child(2) td ul:last-child,
  [class=wrapper] .three-col .column:last-child table:nth-last-child(2) td ul:last-child {
    Margin-bottom: 24px !important;
  }
  [class=wrapper] .header,
  [class=wrapper] .preheader,
  [class=wrapper] .logo,
  [class=wrapper] .footer,
  [class=wrapper] .sidebar {
    width: 320px !important;
  }
  [class=wrapper] .header .logo {
    padding-bottom: 32px !important;
    padding-top: 12px !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
  }
  [class=wrapper] .header .logo img {
    max-width: 280px !important;
    height: auto !important;
  }
  [class=wrapper] .header .preheader {
    padding-top: 3px !important;
    padding-bottom: 22px !important;
  }
  [class=wrapper] .header .title {
    display: none !important;
  }
  [class=wrapper] .header .webversion {
    text-align: center !important;
  }
  [class=wrapper] .footer .address,
  [class=wrapper] .footer .permission {
    width: 280px !important;
  }
  [class=wrapper] h1 {
    font-size: 40px !important;
    Margin-bottom: 20px !important;
  }
  [class=wrapper] h2 {
    font-size: 24px !important;
    Margin-bottom: 16px !important;
  }
  [class=wrapper] h3 {
    font-size: 18px !important;
    Margin-bottom: 12px !important;
  }
  [class=wrapper] .column p,
  [class=wrapper] .column ol,
  [class=wrapper] .column ul {
    font-size: 15px !important;
  }
  [class=wrapper] ol,
  [class=wrapper] ul {
    Margin-left: 20px !important;
  }
  [class=wrapper] li {
    padding-left: 2px !important;
  }
  [class=wrapper] blockquote {
    border-left-width: 4px !important;
    padding-left: 18px !important;
  }
  [class=wrapper] .btn,
  [class=wrapper] .two-col .btn,
  [class=wrapper] .three-col .btn,
  [class=wrapper] .narrower .btn,
  [class=wrapper] .wider .btn {
    Margin-bottom: 27px !important;
  }
  [class=wrapper] .btn a,
  [class=wrapper] .two-col .btn a,
  [class=wrapper] .three-col .btn a,
  [class=wrapper] .narrower .btn a,
  [class=wrapper] .wider .btn a {
    display: block !important;
    font-size: 14px !important;
    letter-spacing: 0.04em !important;
    line-height: 21px !important;
    padding: 9px 22px 8px 22px !important;
  }
  [class=wrapper] table.border {
    width: 320px !important;
  }
  [class=wrapper] .divider {
    margin-bottom: 24px !important;
  }
  [class=wrapper] .column-bottom {
    font-size: 26px !important;
    line-height: 26px !important;
  }
  [class=wrapper] .first .column-bottom,
  [class=wrapper] .second .column-top,
  [class=wrapper] .three-col .second .column-bottom,
  [class=wrapper] .third .column-top {
    display: none;
  }
  [class=wrapper] .social td {
    display: block !important;
    text-align: center !important;
  }
}
@media only screen and (max-width: 320px) {
  td[class=border] {
    display: none;
  }
}
@media (-webkit-min-device-pixel-ratio: 1.5), (min-resolution: 144dpi) {
  .one-col ul {
    border-left: 30px solid #ffffff;
  }
}
</style>
    <!--[if gte mso 9]>
    <style>
      .column-top {
        mso-line-height-rule: exactly !important;
      }
    </style>
    <![endif]-->
  <meta name="robots" content="noindex,nofollow" />
<meta property="og:title" content="My First Campaign" />
</head>
  <body style="margin: 0;mso-line-height-rule: exactly;padding: 0;min-width: 100%;background-color: #f5f7fa"><style type="text/css">
@import url(https://fonts.googleapis.com/css?family=Lato:400,700,400italic,700italic);@import url(https://fonts.googleapis.com/css?family=Lato:400,700,400italic,700italic);@import url(https://fonts.googleapis.com/css?family=Lato:400,700,400italic,700italic);@import url(https://fonts.googleapis.com/css?family=Open+Sans:400italic,700italic,700,400);@import url(https://fonts.googleapis.com/css?family=Open+Sans:400italic,700italic,700,400);@import url(https://fonts.googleapis.com/css?family=Lato:400,700,400italic,700italic);body,.wrapper,.emb-editor-canvas{background-color:#f5f7fa}.border{background-color:#dddee1}h1{color:#44a8c7}.wrapper h1{}.wrapper h1{font-family:Tahoma,sans-serif}@media only screen and (min-width: 0){.wrapper h1{font-family:Lato,Tahoma,sans-serif !important}}h1{}.one-col h1{line-height:50px}.two-col h1,.wider h1{line-height:36px}.three-col h1,.narrower 
h1{line-height:30px}@media only screen and (max-width: 620px){h1{line-height:50px !important}}h2{color:#44a8c7}.wrapper h2{}.wrapper h2{font-family:Tahoma,sans-serif}@media only screen and (min-width: 0){.wrapper h2{font-family:Lato,Tahoma,sans-serif !important}}h2{}.one-col h2{line-height:32px}.two-col h2,.wider h2{line-height:28px}.three-col h2,.narrower h2{line-height:24px}@media only screen and (max-width: 620px){h2{line-height:32px !important}}h3{color:#3b3e42}.wrapper h3{}.wrapper h3{font-family:Tahoma,sans-serif}@media only screen and (min-width: 0){.wrapper h3{font-family:Lato,Tahoma,sans-serif !important}}h3{}.one-col h3{line-height:26px}.two-col h3,.wider h3{line-height:23px}.three-col h3,.narrower h3{line-height:21px}@media only screen and (max-width: 620px){h3{line-height:26px !important}}p,ol,ul{color:#60666d}.wrapper p,.wrapper ol,.wrapper ul{}.wrapper p,.wrapper 
ol,.wrapper ul{font-family:sans-serif}@media only screen and (min-width: 0){.wrapper p,.wrapper ol,.wrapper ul{font-family:"Open Sans",sans-serif !important}}p,ol,ul{}.one-col p,.one-col ol,.one-col ul{line-height:24px;Margin-bottom:24px}.two-col p,.two-col ol,.two-col ul,.wider p,.wider ol,.wider ul{line-height:21px;Margin-bottom:21px}.three-col p,.three-col ol,.three-col ul,.narrower p,.narrower ol,.narrower ul{line-height:20px;Margin-bottom:20px}@media only screen and (max-width: 620px){p,ol,ul{line-height:24px !important;Margin-bottom:24px !important}}.image{color:#60666d}.image{font-family:sans-serif}@media only screen and (min-width: 0){.image{font-family:"Open Sans",sans-serif !important}}.wrapper a{color:#5c91ad}.wrapper a:hover{color:#48768e !important}.wrapper .btn a{color:#fff;background-color:#5c91ad;box-shadow:0 3px 0 #4a748a}.wrapper .btn a{font-family:sans-serif}@media 
only screen and (min-width: 0){.wrapper .btn a{font-family:"Open Sans",sans-serif !important}}.wrapper .btn a:hover{box-shadow:inset 0 1px 2px #4a748a !important;color:#fff !important}.wrapper p a,.wrapper ol a,.wrapper ul a{border-bottom:1px dotted #5c91ad}.wrapper blockquote{border-left:4px solid #f5f7fa}.wrapper .three-col blockquote,.wrapper .narrower blockquote{border-left:2px solid #f5f7fa}.logo div{color:#555}.wrapper .logo div{}.wrapper .logo div{font-family:Tahoma,sans-serif}@media only screen and (min-width: 0){.wrapper .logo div{font-family:Lato,Tahoma,sans-serif !important}}.logo div a{color:#555}.logo div a:hover{color:#555 !important}.preheader,.footer{color:#b9b9b9}.preheader,.footer{font-family:sans-serif}@media only screen and (min-width: 0){.preheader,.footer{font-family:"Open Sans",sans-serif !important}}.wrapper .preheader a,.wrapper .footer a{color:#b9b9b9}.wrapper 
.preheader a:hover,.wrapper .footer a:hover{color:#b9b9b9 !important}.footer .social a{}.wrapper .footer .social a{}.wrapper .footer .social a{font-family:sans-serif}@media only screen and (min-width: 0){.wrapper .footer .social a{font-family:"Open Sans",sans-serif !important}}.footer .social a{}.footer .social a{font-weight:600}
</style>
    <center class="wrapper" style="display: table;table-layout: fixed;width: 100%;min-width: 620px;-webkit-text-size-adjust: 100%;-ms-text-size-adjust: 100%;background-color: #f5f7fa">
        
            <table class="border" style="border-collapse: collapse;border-spacing: 0;font-size: 1px;line-height: 1px;background-color: #dddee1;Margin-left: auto;Margin-right: auto" width="602">
              <tbody><tr><td style="padding: 0;vertical-align: top">&#8203;</td></tr>
            </tbody></table>
          
            <table class="centered" style="border-collapse: collapse;border-spacing: 0;Margin-left: auto;Margin-right: auto">
              <tbody><tr>
                <td class="border" style="padding: 0;vertical-align: top;font-size: 1px;line-height: 1px;background-color: #dddee1;width: 1px">&#8203;</td>
                <td style="padding: 0;vertical-align: top">
                  <table class="one-col" style="border-collapse: collapse;border-spacing: 0;Margin-left: auto;Margin-right: auto;width: 600px;background-color: #ffffff;table-layout: fixed">
                    <tbody><tr>
                      <td class="column" style="padding: 0;vertical-align: top;text-align: left">
                        
              <div class="image" style="font-size: 12px;Margin-bottom: 24px;mso-line-height-rule: at-least;color: #60666d;font-family: sans-serif; background-color: #f8f8f8;" align="center">
                <a style="text-decoration: none;color: #5c91ad" href=\"""" + str(website_hostname) + """\"><img style="border: 0;-ms-interpolation-mode: bicubic;display: block;max-width: 600px" src=\"""" + str(website_hostname) + str(RELATIVE_STATIC_URL) + """img/email_banner.jpg\" alt=\"""" + str(website_name) + """: online language assessment for longitudinal monitoring of changes in cognition\" width="600" height="80" /></a>
              </div>
            
                          <table class="contents" style="border-collapse: collapse;border-spacing: 0;table-layout: fixed;width: 100%">
                            <tbody><tr>
                              <td class="padded" style="padding: 0;vertical-align: top;padding-left: 50px;padding-right: 50px;word-break: break-word;word-wrap: break-word">
                                
              <div style="height:15px">&nbsp;</div>
            
                              </td>
                            </tr>
                          </tbody></table>
                        
                          <table class="contents" style="border-collapse: collapse;border-spacing: 0;table-layout: fixed;width: 100%">
                            <tbody><tr>
                              <td class="padded" style="padding: 0;vertical-align: top;padding-left: 50px;padding-right: 50px;word-break: break-word;word-wrap: break-word">"""
                                
emailPost = """</td>
                            </tr>
                          </tbody></table>
                        
                        <div class="column-bottom" style="font-size: 26px;line-height: 26px">&nbsp;</div>
                      </td>
                    </tr>
                  </tbody></table>
                </td>
                <td class="border" style="padding: 0;vertical-align: top;font-size: 1px;line-height: 1px;background-color: #dddee1;width: 1px">&#8203;</td>
              </tr>
            </tbody></table>
          
            <table class="border" style="border-collapse: collapse;border-spacing: 0;font-size: 1px;line-height: 1px;background-color: #dddee1;Margin-left: auto;Margin-right: auto" width="602">
              <tbody><tr><td style="padding: 0;vertical-align: top">&nbsp;</td></tr>
            </tbody></table>
          
        <table class="centered" style="border-collapse: collapse;border-spacing: 0;Margin-left: auto;Margin-right: auto">
          <tbody><tr>
            <td class="footer" style="padding: 0;vertical-align: top;letter-spacing: 0.01em;font-style: normal;line-height: 17px;font-weight: 400;font-size: 11px;Margin-right: auto;Margin-left: auto;padding-top: 50px;padding-bottom: 40px;width: 602px;color: #b9b9b9;font-family: sans-serif">
              <center>
                <div class="address" style="Margin-bottom: 19px">SPOClab: Signal Processing and Oral Communication lab<br />
550 University Avenue, 12-175<br />
Toronto, Ontario&nbsp;M5G 2A2<br />
<a href="http://spoclab.ca">http://spoclab.ca</a></div>
                <div class="permission" style="Margin-bottom: 10px">You are receiving this email due to your account preferences. To unsubscribe, please visit your <a href='""" + str(website_hostname) + '/account' + """'>Account Settings page</a>.</div>
              </center>
            </td>
          </tr>
        </tbody></table>
      </center>
  
</body></html>
"""

# emailFrom: string, the email used to send out the emails
# nameFrom: string, how the 'from' appears in the email (e.g., "Talk2Me")
# emailTo, emailCc, emailBcc: lists of email addresses
# emailSubject, text, html: strings
def sendEmail(emailFrom, nameFrom, emailTo, emailCc, emailBcc, emailSubject, text, html):
    # Send the message using sendmail
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = emailSubject
        msg['From'] = nameFrom + "<" + emailFrom + ">"
        msg['To'] = ",".join(emailTo)
        msg['Cc'] = ",".join(emailCc)
        msg['Bcc'] = ",".join(emailBcc)

        # Create an HTML and alternate plain text version
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
        
        p = Popen(["/usr/sbin/sendmail", "-t"], stdin=PIPE)
        p.communicate(msg.as_string())
            
        return True
    except:
        return False
