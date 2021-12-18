-- Copyright 2021 The Mumble Developers. All rights reserved.
-- Use of this source code is governed by a BSD-style license
-- that can be found in the LICENSE file at the root of the
-- Mumble source tree or at <https://www.mumble.info/LICENSE>.

local musage = require "musage"
local xmlutils = require "xmlutils"

function handle(r)
	if r.method ~= "POST" then
		return 405
	end

	local root = xmlutils.get_root(r:requestbody())
	if not root then
		return 400
	end

	local usage = root.usage
	if not usage then
		return 400
	end

	local database, error = r:dbacquire("mod_dbd")
	if error then
		r:err("Failed to connect to SQL database: " .. error)
		return 500
	end

	local status = musage.store(database, 1, r, usage)

	database:close()

	return status
end
