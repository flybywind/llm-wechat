import { library } from "@fortawesome/fontawesome-svg-core";
import { faPencilAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { createApp } from "vue";
import "./assets/styles/main.scss";
import App from "./App.vue";

library.add(faPencilAlt);

document.addEventListener(
  "deviceready",
  function () {
    console.log("Cordova is ready!");
    // 您的 Cordova 相关代码
    window.resolveLocalFileSystemURL(
      cordova.file.dataDirectory,
      function (dirEntry) {
        console.log("file system open: " + dirEntry.name);
        // var isAppend = true;
        // createFile(dirEntry, "fileToAppend.txt", isAppend);
      }
      // onErrorLoadFs
    );
  },
  false
);

const app = createApp(App);
app.component("font-awesome-icon", FontAwesomeIcon);
app.mount("#app");
