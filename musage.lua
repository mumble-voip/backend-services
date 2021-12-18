-- Copyright 2021 The Mumble Developers. All rights reserved.
-- Use of this source code is governed by a BSD-style license
-- that can be found in the LICENSE file at the root of the
-- Mumble source tree or at <https://www.mumble.info/LICENSE>.

local xmlutils = require "xmlutils"

local musage = {}

function musage.store(database, is_client, request, xml)
	local machash = xmlutils.get_value("machash", xml)
	if not machash or string.len(machash) ~= 40 then
		return 400
	end

	statement, error = database:prepare(request, "REPLACE INTO musage (client, ip, arch, version, compiled, os, osarch, osver, osverbose, qt, insys, outsys, lcd, machash, cpu_id, cpu_extid, cpu_sse2) VALUES(%u, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
	if error then
		return 500
	end

	local arch = xmlutils.get_value("arch", xml)
	local cpu_id = xmlutils.get_value("cpu_id", xml)
	local cpu_extid = xmlutils.get_value("cpu_extid", xml)
	local cpu_sse2 = xmlutils.get_value("cpu_sse2", xml)
	local insys = xmlutils.get_value("in", xml)
	local lcd = xmlutils.get_value("lcd", xml)
	local os = xmlutils.get_value("os", xml)
	local osarch = xmlutils.get_value("osarch", xml)
	local osver = xmlutils.get_value("osver", xml)
	local osverbose = xmlutils.get_value("osverbose", xml)
	local outsys = xmlutils.get_value("out", xml)
	local qt = xmlutils.get_value("qt", xml)
	local release = xmlutils.get_value("release", xml)
	local version = xmlutils.get_value("version", xml)

	if not arch then
		if os == "WinX64" then
			arch = "x64"
			os = "Windows"
		elseif os == "Win" then
			arch = "x86"
			os = "Windows"
		else
			local is64bit = xmlutils.get_value("is64bit", xml)
			if is64bit == "1" then
				arch = "64 bit"
			elseif is64bit == "0" then
				arch = "32 bit"
			end
		end
	end

	if os == "X11" then
		os = "UNIX"
	end

	result, error = statement:query(is_client, request.useragent_ip, arch, version, release, os, osarch, osver, osverbose, qt, insys, outsys, lcd, machash, cpu_id, cpu_extid, cpu_sse2)
	if error then
		return 500
	end

	return 200
end

return musage
