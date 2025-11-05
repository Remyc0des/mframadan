local M = {}

function M.list()
  local output = vim.fn.systemlist("todo list")
  vim.cmd("new")
  vim.api.nvim_buf_set_lines(0, 0, -1, false, output)
  vim.bo.bufftype = "nofile"
  vim.bo.bufhidden = "wipe"
  vim.bo.swipefile = false
end


function M.add()
  local title = vim.fn.input("Task: ")
  vim.fn.system("todo add \"" .. title .. "\"")
  print("Added: " .. title)
end

function M.setup()
  vim.api.nvim_create_user_command("TodoList", M.list, {})
  vim.api.nvim_create_user_command("TodoAdd", M.add, {})
end

return M
