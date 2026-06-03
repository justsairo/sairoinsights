module.exports = {
  run: [
    {
      method: "fs.rm",
      params: {
        path: "app/backend/env"
      }
    },
    {
      method: "fs.rm",
      params: {
        path: "app/frontend/node_modules"
      }
    },
    {
      method: "fs.rm",
      params: {
        path: "app/frontend/dist"
      }
    },
    {
      method: "fs.rm",
      params: {
        path: "app/automation"
      }
    }
  ]
}
