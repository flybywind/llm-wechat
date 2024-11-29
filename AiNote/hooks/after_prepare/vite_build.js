#!/usr/bin/env node

const { exec } = require("child_process");

module.exports = function (ctx) {
  console.log("Building Vite app...");
  exec("npm run build", { cwd: "vite-vue" }, (error, stdout, stderr) => {
    if (error) {
      console.error(`Vite build error: ${stderr}`);
    } else {
      console.log("Vite build complete");
    }
  });
};
