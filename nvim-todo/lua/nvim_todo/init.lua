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

function M.canvaspull()
  local canvas = vim.fn.system('todo canvaslist')
  print("Added task from canvas!")
  print("current task list:")
  M.list()
end


function M.setup()
  vim.api.nvim_create_user_command("TodoList", M.list, {})
  vim.api.nvim_create_user_command("TodoAdd", M.add, {})
  vim.api.nvim_create_user_command("TodoPull", M.canvaspull, {})
end



return M
