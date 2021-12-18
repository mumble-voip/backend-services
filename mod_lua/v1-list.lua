-- Copyright 2021 The Mumble Developers. All rights reserved.
-- Use of this source code is governed by a BSD-style license
-- that can be found in the LICENSE file at the root of the
-- Mumble source tree or at <https://www.mumble.info/LICENSE>.

require "continent"

local ip2location = require "ip2location"
local lfs = require "lfs"

local life = 1800
local listpath = "/tmp/v1-list.xml"
local dbpath = "ip2location-lite-db3.bin"

function handle(r)
	r.content_type = "text/xml"

	local regenerate = false
	local lastedit, error = lfs.attributes(listpath, "modification")
	if error or (lastedit + life) <= os.time() then
		regenerate = true
	end

	if not regenerate then
		local file = assert(io.open(listpath, "r"))
		local content = assert(file:read("*all"))
		r:write(content)
		file.close()

		return apache2.OK
	end

	local ip2loc = assert(ip2location:new(dbpath))

	local database, error = r:dbacquire("mod_dbd")
	if error then
		r:err("Failed to connect to SQL database: " .. error)
		return 500
	end

	local result, error = database:select(r, "SELECT name, ip, geoip, port, url, verify FROM servers WHERE seen + interval 24 hour > now() ORDER BY name")
	if error then
		r:err("Failed to run SQL query: " .. error)
		return 500
	end

	local rows = result(0)

	database:close()

	local xml = { }

	xml[#xml + 1] = "<?xml version='1.0' standalone='yes'?>"
	xml[#xml + 1] = "<servers>"

	for _, row in ipairs(rows) do
		local result = ip2loc:get_all(row[3])
		local server = { }

		server[#server + 1] = "\t<server"
		server[#server + 1] = string.format("name=\"%s\"", r:escape_html(row[1]))
		server[#server + 1] = string.format("ca=\"%s\"", row[6])
		server[#server + 1] = string.format("continent_code=\"%s\"", continent[result.country_short])
		server[#server + 1] = string.format("country=\"%s\"", result.country_long)
		server[#server + 1] = string.format("country_code=\"%s\"", result.country_short)
		server[#server + 1] = string.format("ip=\"%s\"", r:escape_html(row[2]))
		server[#server + 1] = string.format("port=\"%s\"", row[4])
		server[#server + 1] = string.format("region=\"%s\"", result.region)
		server[#server + 1] = string.format("url=\"%s\"", r:escape_html(row[5]))
		server[#server + 1] = "/>"

		xml[#xml + 1] = table.concat(server, " ")
	end

	ip2loc:close()

	xml[#xml + 1] = "</servers>"

	local string = table.concat(xml, "\n")
	r:write(string)

	local file = assert(io.open(listpath, "w"))
	file:write(string)
	file:close()

	return apache2.OK
end
