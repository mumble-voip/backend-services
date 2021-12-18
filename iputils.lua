-- Copyright 2021 The Mumble Developers. All rights reserved.
-- Use of this source code is governed by a BSD-style license
-- that can be found in the LICENSE file at the root of the
-- Mumble source tree or at <https://www.mumble.info/LICENSE>.

-- The IP validation algorithms are from:
-- https://it.wikipedia.org/wiki/Modulo:IP_validator

local iputils = {}

function iputils.is_ipv4(str)
	str = str:gsub("/[0-9]$", ""):gsub("/[12][0-9]$", ""):gsub("/[3][0-2]$", "")

	if not str:find("^%d+%.%d+%.%d+%.%d+$") then
		return false
	end

	for substr in str:gmatch("(%d+)") do
		if not substr:find("^[1-9]?[0-9]$") and not substr:find("^1[0-9][0-9]$") and not substr:find("^2[0-4][0-9]$") and not substr:find("^25[0-5]$") then
			return false
		end
	end

	return true
end

function iputils.is_ipv6(str)
	if not (str:find("^%w+:%w+:%w+:%w+:%w+:%w+:%w+:%w+$") or (str:find("^%w*:%w*:%w*:?%w*:?%w*:?%w*:?%w*$") and str:find("::"))) or str:find("::.*::") or str:find(":::") then
		return false
	end

	for substr in str:gmatch("(%w+)") do
		if not substr:find("^[0-9A-Fa-f][0-9A-Fa-f]?[0-9A-Fa-f]?[0-9A-Fa-f]?$") then
			return false
		end
	end

	return true
end

function iputils.is_ip(str)
	return iputils.is_ipv4(str) or iputils.is_ipv6(str)
end

return iputils
