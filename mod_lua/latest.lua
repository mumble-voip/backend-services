-- Copyright 2021 The Mumble Developers. All rights reserved.
-- Use of this source code is governed by a BSD-style license
-- that can be found in the LICENSE file at the root of the
-- Mumble source tree or at <https://www.mumble.info/LICENSE>.

local json = require "json"

local client_filepath = "client-version.json"
local server_filepath = "server-version.json"

function handle(r)
	local local_path = r.uri
	if not local_path then
		return apache2.DECLINED
	end

	local type, product, os, arch = string.match(local_path, "/latest/(%w+)/(%w+)-(.+)-(%w+)")
	if not type or not product or not os or not arch then
		return apache2.DECLINED
	end

	local filepath
	if product == "client" then
		filepath = client_filepath
	elseif product == "server" then
		filepath = server_filepath
	else
		return apache2.DECLINED
	end

	local file = assert(io.open(filepath, "r"))
	local content = file:read("*a")
	file:close()

	local table = json.decode(content)
	if not table or not table[type] then
		return apache2.DECLINED
	end

	local type_table = table[type]
	if not type_table[os] then
		return apache2.DECLINED
	end

	local os_table = type_table[os]
	if not os_table[arch] then
		return apache2.DECLINED
	end

	local arch_table = os_table[arch]
	if not arch_table["url"] then
		return apache2.DECLINED
	end

	local url = arch_table["url"]
	local_path = string.gsub(url, "https://dl.mumble.info", "")
	if not local_path then
		return apache2.DECLINED
	end

	r.filename = r.document_root .. local_path

	local basename = url:match(".+/(.*)$")
	r.headers_out["content-disposition"] = "attachment; filename=" .. basename

	return apache2.OK
end
