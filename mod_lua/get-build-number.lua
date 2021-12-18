-- Copyright 2021 The Mumble Developers. All rights reserved.
-- Use of this source code is governed by a BSD-style license
-- that can be found in the LICENSE file at the root of the
-- Mumble source tree or at <https://www.mumble.info/LICENSE>.

local json = require "json"
local openssl = require "openssl"

local filepath = "build-number.json"

local allowed_hashes = {
	-- "Token"
	["3ab72857dbcf918f58f9c40be8f1ea4d079e67e2bfb040d7da714522ca885cd531145537848121be5b825e99f042338d26b66384e86c8183c00ad6fc95862636"] = true
}

local function hash_token(token)
	local md = openssl.digest.get("blake2b512")
	local digest = md:digest(token)
	return openssl.hex(digest)
end

local function is_parameter_ok(parameter)
	-- The value is empty with "?parameter=".
	-- The value is "1" with "?parameter".
	if not parameter or parameter == "" or parameter == "1" then
		return false
	end

	return true
end

function handle(r)
	r.content_type = "text/html"

	if r.method ~= "GET" then
		return 405
	end

	local args = r:parseargs()

	local token = args["token"]
	if not is_parameter_ok(token) or not allowed_hashes[hash_token(token)] then
		return 401
	end

	local commit = args["commit"]
	if not is_parameter_ok(commit) then
		r:write("Missing \"commit\" parameter!\n")
		r.status = 400
		return apache2.OK
	end

	local version = args["version"]
	if not is_parameter_ok(version) then
		r:write("Missing \"version\" parameter!\n")
		r.status = 400
		return apache2.OK
	end

	local file = assert(io.open(filepath, "r"))
	local content = file:read("*a")
	file:close()

	local table = json.decode(content)
	if not table then
		table = { }
	end

	if not table[version] then
		table[version] = { ["current"] = -1 }
	end

	if not table[version][commit] then
		table[version]["current"] = table[version]["current"] + 1
		table[version][commit] = table[version]["current"]
	end

	r:write(table[version][commit])

	content = json.encode(table) .. "\n"

	file = assert(io.open(filepath, "w"))
	file:write(content)
	file:close()	

	return apache2.OK
end
