-- Copyright 2021 The Mumble Developers. All rights reserved.
-- Use of this source code is governed by a BSD-style license
-- that can be found in the LICENSE file at the root of the
-- Mumble source tree or at <https://www.mumble.info/LICENSE>.

local https = require "ssl.https"
local lfs = require "lfs"

local life = 3600
local localdir = "/tmp"

function handle(r)
	r:err(r.uri)

	if r.uri ~= "/AUTHORS" and r.uri ~= "/LICENSE" then
		return 404
	end

	local filepath = localdir .. r.uri
	local regenerate = false

	local lastedit, error = lfs.attributes(filepath, "modification")
	if error or (lastedit + life) <= os.time() then
		regenerate = true
	end

	if not regenerate then
		local file = assert(io.open(filepath, "r"))
		local content = assert(file:read("*all"))
		r:write(content)
		file.close()

		return apache2.OK
	end

	local page, status_code = https.request("https://raw.githubusercontent.com/mumble-voip/mumble/master" .. r.uri)
	r:write(page)

	if status_code ~= 200 then
		r:err("Bad status code received from GitHub: " .. status_code)
		return apache2.OK
	end

	local file = assert(io.open(filepath, "w"))
	file:write(page)
	file:close()

	return apache2.OK
end
