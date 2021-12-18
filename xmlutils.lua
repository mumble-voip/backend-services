-- Copyright 2021 The Mumble Developers. All rights reserved.
-- Use of this source code is governed by a BSD-style license
-- that can be found in the LICENSE file at the root of the
-- Mumble source tree or at <https://www.mumble.info/LICENSE>.

local xml2lua = require "xml2lua"
local xmlhandler = require "xmlhandler.tree"

local xmlutils = {}

function xmlutils.get_root(xml)
	local parser = xml2lua.parser(xmlhandler)
	parser:parse(xml, WS_NORMALIZE)

	return xmlhandler.root
end

function xmlutils.get_value(key, xml)
	if type(xml[key]) == "string" then
		-- Single instance.
		return xml[key]
	elseif type(xml[key]) == "table" then
		if #xml[key] > 0 then
			-- Multiple instances, choose first one.
			return xml[key][1]
		else
			return nil
		end
	end

	return nil
end

return xmlutils
