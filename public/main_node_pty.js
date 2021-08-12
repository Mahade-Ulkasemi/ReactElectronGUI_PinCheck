const { app, BrowserWindow, ipcMain, Menu } = require("electron");
const { dialog } = require("electron");
const path = require("path");
const is = require("electron-is");
const isDev = require("electron-is-dev");
const pty = require("node-pty");
const findProcess = require("find-process");
const ps = require("ps-node");
const os = require("os");
const PDFWindow = require("electron-pdf-window");
var shell = is.windows() ? "powershell.exe" : "bash";
const fs = require("fs");

function createWindow() {
  // Create the browser window.
  const win = new BrowserWindow({
    width: 700,
    height: 600,
    minWidth: 700,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      enableRemoteModule: true,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  win.loadURL(
    isDev
      ? "http://localhost:3000"
      : `file://${path.join(__dirname, "../build/index.html")}`
  );

  // MENU BAR
  var menu = Menu.buildFromTemplate([
    {
      label: "File",
      submenu: [
        {
          label: "Exit",
          click() {
            app.quit();
          },
        },
      ],
    },
    {
      label: "Edit",
      submenu: [
        {
          label: "Undo",
          accelerator: "CmdOrCtrl+Z",
          role: "undo",
        },
        {
          label: "Redo",
          accelerator: "Shift+CmdOrCtrl+Z",
          role: "redo",
        },
        {
          type: "separator",
        },
        {
          label: "Cut",
          accelerator: "CmdOrCtrl+X",
          role: "cut",
        },
        {
          label: "Copy",
          accelerator: "CmdOrCtrl+C",
          role: "copy",
        },
        {
          label: "Paste",
          accelerator: "CmdOrCtrl+V",
          role: "paste",
        },
        {
          label: "Select All",
          accelerator: "CmdOrCtrl+A",
          role: "selectall",
        },
      ],
    },
    {
      label: "View",
      submenu: [
        {
          label: "Reload",
          accelerator: "CmdOrCtrl+R",
          click: function (item, focusedWindow) {
            if (focusedWindow) focusedWindow.reload();
          },
        },
        {
          label: "Force Reload",
          accelerator: "CmdOrCtrl+Shift+R",
          click: function (item, focusedWindow) {
            if (focusedWindow) focusedWindow.reload();
          },
        },
        {
          label: "Toggle Full Screen",
          accelerator: (function () {
            if (process.platform == "darwin") return "Ctrl+Command+F";
            else return "F11";
          })(),
          click: function (item, focusedWindow) {
            if (focusedWindow)
              focusedWindow.setFullScreen(!focusedWindow.isFullScreen());
          },
        },
        {
          label: "Toggle Developer Tools",
          accelerator: (function () {
            if (process.platform == "darwin") return "Alt+Command+I";
            else return "Ctrl+Shift+I";
          })(),
          click: function (item, focusedWindow) {
            if (focusedWindow) focusedWindow.toggleDevTools();
          },
        },
      ],
    },
    {
      label: "Window",
      role: "window",
      submenu: [
        {
          label: "Minimize",
          accelerator: "CmdOrCtrl+M",
          role: "minimize",
        },
        {
          label: "Close",
          accelerator: "CmdOrCtrl+W",
          role: "close",
        },
      ],
    },
    {
      label: "Help",
      role: "help",
      submenu: [
        {
          label: "Documentation",
          click: function () {
            require("electron").shell.openPath(
              `${path.join(__dirname, "Scripts/pin_check/pin_check.pdf")}`
            );
            // const Pdfwin = new PDFWindow({
            //   width: 800,
            //   height: 600,
            // });
            // Pdfwin.setMenu(null);
            // Pdfwin.loadURL(
            //   `file://${path.join(
            //     __dirname,
            //     "Scripts/pin_check/pin_check.pdf"
            //   )}`
            // );
          },
        },
      ],
    },
  ]);
  Menu.setApplicationMenu(menu);

  //

  // File selector
  ipcMain.on("fileSelector.dialog", (event, values) => {
    dialog
      .showOpenDialog(win, {
        properties: ["openFile"],
      })
      .then((result) => {
        console.log(result.canceled);
        console.log(result.filePaths);
        console.log(values);
        win.webContents.send(
          "selected-file",
          result.filePaths,
          values,
          result.canceled
        );
      })
      .catch((err) => {
        console.log(err);
      });
  });

  // Directory selector
  ipcMain.on("directorySelector.dialog", (event, values) => {
    dialog
      .showOpenDialog(win, {
        properties: ["openDirectory"],
      })
      .then((result) => {
        console.log(result.canceled);
        console.log(result.filePaths);
        console.log(values);
        win.webContents.send(
          "selected-directory",
          result.filePaths,
          values,
          result.canceled
        );
      })
      .catch((err) => {
        console.log(err);
      });
  });

  // Event Listeners & Run Python Script
  ipcMain.on("terminal.cmd", (event, values) => {
    console.log(values);

    // Check CWD Exist
    // check if directory exists
    if (fs.existsSync(values["output_directory"])) {
      console.log("Output Directory exists!");
    } else {
      console.log("Output Directory not found. Creating Output Directory!!!");
      fs.mkdirSync(values["output_directory"], { recursive: true });
    }

    // Access shell using node-pty
    const settings = {
      name: "xterm",
      cols: values["cols"] - 2,
      rows: values["rows"] - 2,
      cwd: values["output_directory"],
      env: process.env,
    };

    if (is.dev) {
      var script_path = `${path.join(
        __dirname,
        "Scripts",
        "pin_check",
        "pinCheckFE.py"
      )}`;
      script_path = '"' + script_path + '"';
    } else {
      var script_path = `${path.join(
        __dirname,
        "..",
        "build",
        "Scripts",
        "pin_check",
        "pinCheckFE.py"
      )}`;
      script_path = '"' + script_path + '"';
    }

    script_args = [
      "python",
      script_path,
      `-i ${values["IP_Type"]} -l ${values["ip_library_path"]}`,
    ];

    var ptyProcess = pty.spawn(shell, script_args, settings);

    ptyProcess.on("data", function (data) {
      win.webContents.send("terminal.log", data);
      // console.log(data.toString());
      console.log("Data sent");
      // console.log(process);
    });
    ptyProcess.on("exit", () => {
      console.log("exit");
      win.webContents.send("process.finish", ptyProcess.pid);
      ipcMain.removeAllListeners("terminal.kill");
    });

    // Kill
    ipcMain.on("terminal.kill", (e, v) => {
      console.log("script pid on kill button click: ", ptyProcess.pid);
      // console.log(ptyProcess);
      findProcess("name", "Electron").then(
        function (list) {
          for (var i = 0; i < list.length; i++) {
            // console.log(list[i]);
            pidToKill = list[i].pid;
            pidToKill = pidToKill.toString();
            ppidToKill = list[i].ppid.toString();

            if (
              pidToKill === ptyProcess.pid.toString() ||
              ppidToKill === ptyProcess.pid.toString()
            ) {
              console.log("PS KILL :: ", pidToKill);
              ps.kill(
                pidToKill,
                {
                  signal: "SIGKILL",
                  // timeout: 10, // will set up a ten seconds timeout if the killing is not successful
                },
                function () {}
              );
            }
          }
        },
        function (err) {
          console.log(err.stack || err);
        }
      );
    });
  });
}

app.on("ready", createWindow);

// Quit when all windows are closed.
app.on("window-all-closed", function () {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", function () {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
