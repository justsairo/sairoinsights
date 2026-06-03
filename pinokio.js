const path = require("path")
const fs = require("fs")

module.exports = {
  version: "7.0",
  title: "Sairo Insights",
  description: "A local data analysis app for uploading, cleaning, analyzing, visualizing, and generating insights from datasets.",
  icon: "icon.svg",
  menu: async (kernel, info) => {
    const installing = info.running("install.js")
    const installed = info.exists("app/backend/env") && info.exists("app/frontend/dist")
    const running = info.running("start.js")
    const updating = info.running("update.js")
    const resetting = info.running("reset.js")

    let n8n_url = "http://localhost:5678"
    try {
      const envPath = path.resolve(__dirname, "app/backend/.env")
      if (fs.existsSync(envPath)) {
        const env = fs.readFileSync(envPath, "utf-8")
        const match = env.match(/N8N_URL=(.+)/)
        if (match) n8n_url = match[1].trim()
      }
    } catch (e) {
      console.log("Error reading .env", e)
    }

    if (installing) {
      return [{
        default: true,
        icon: "fa-solid fa-plug",
        text: "Installing",
        href: "install.js"
      }]
    }

    if (!installed) {
      return [{
        default: true,
        icon: "fa-solid fa-plug",
        text: "Install",
        href: "install.js"
      }]
    }

    if (running) {
      const local = kernel.memory.local[path.resolve(__dirname, "start.js")]
      const items = []
      if (local && local.url) {
        items.push({
          default: true,
          icon: "fa-solid fa-rocket",
          text: "Open Web UI",
          href: local.url
        })
      } else {
        items.push({
          default: true,
          icon: "fa-solid fa-terminal",
          text: "Terminal",
          href: "start.js"
        })
      }

      items.push({
        icon: "fa-solid fa-network-wired",
        text: "Automation (n8n)",
        href: n8n_url,
        target: "_blank"
      })

      if (local && local.url) {
        items.push({
          icon: "fa-solid fa-terminal",
          text: "Terminal",
          href: "start.js"
        })
      }
      return items
    }

    if (updating) {
      return [{
        default: true,
        icon: "fa-solid fa-arrows-rotate",
        text: "Updating",
        href: "update.js"
      }]
    }

    if (resetting) {
      return [{
        default: true,
        icon: "fa-solid fa-broom",
        text: "Resetting",
        href: "reset.js"
      }]
    }

    const base_menu = [{
      default: true,
      icon: "fa-solid fa-power-off",
      text: "Start",
      href: "start.js"
    }, {
      icon: "fa-solid fa-network-wired",
      text: "Automation (n8n)",
      href: n8n_url,
      target: "_blank"
    }]

    if (info.exists("app/automation/sairo_insights_workflow.json")) {
      base_menu.push({
        icon: "fa-solid fa-file-code",
        text: "Automation Workflow",
        href: "app/automation/sairo_insights_workflow.json",
        target: "_blank"
      })
    }

    base_menu.push({
      icon: "fa-solid fa-arrows-rotate",
      text: "Update",
      href: "update.js"
    }, {
      icon: "fa-solid fa-plug",
      text: "Install",
      href: "install.js"
    }, {
      icon: "fa-solid fa-broom",
      text: "Factory Reset",
      href: "reset.js"
    })

    return base_menu
  }
}
