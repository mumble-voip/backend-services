-- Copyright 2021 The Mumble Developers. All rights reserved.
-- Use of this source code is governed by a BSD-style license
-- that can be found in the LICENSE file at the root of the
-- Mumble source tree or at <https://www.mumble.info/LICENSE>.

local dnsutils = require "dnsutils"
local iputils = require "iputils"
local musage = require "musage"
local openssl = require "openssl"
local xmlutils = require "xmlutils"

local function hash(password)
	local md = openssl.digest.get("sha1")
	local sha1 = md:digest(password)
	return openssl.hex(sha1)
end

local function test_address(certificate, address, r)
	local ctx = openssl.ssl.ctx_new("TLS_client")
	ctx:verify_locations("/etc/ssl/certs/ca-certificates.crt", "/etc/ssl/certs")

	local socket = openssl.bio.connect(address, false)
	if not socket then
		r:err(string.format("openssl.bio.connect() failed to connect to %s: %s", address, openssl.error()))
		return false
	end

	if not socket:connect() then
		r:err(string.format("socket:connect() failed to connect to %s: %s", address, openssl.error()))
		return false
	end

	local ssl = ctx:ssl(socket)
	if not ssl:connect() then
		r:err(string.format("ssl:connect() failed: %s", openssl.error()))
		return false
	end

	if certificate ~= ssl:peer():export() then
		r:write("Unmatching certificate! Is there perhaps another server?\n")
		return false
	end

	local verified = ssl:getpeerverification()

	ssl:shutdown()
	socket:shutdown()
	socket:close()

	return true, verified
end

function handle(r)
	if r.method ~= "POST" then
		return 405
	end

	local certificate = r:subprocess_env_table()["SSL_CLIENT_CERT"]
	if not certificate then
		r:write("Missing certificate!")
		r.status = 496
		return apache2.OK
	end

	local root = xmlutils.get_root(r:requestbody())
	if not root then
		return 400
	end

	local server = root.server
	if not server then
		return 400
	end

	local digest = xmlutils.get_value("digest", server)
	local name = xmlutils.get_value("name", server)
	local password = xmlutils.get_value("password", server)
	local port = xmlutils.get_value("port", server)
	local url = xmlutils.get_value("url", server)

	if not digest or not name or not password or not port or not url then
		r:write("Missing data in registration request!\n")
		r.status = 400
		return apache2.OK
	end

	local addresses = { }
	
	local hostname = xmlutils.get_value("host", server)
	if not hostname then
		hostname = r.useragent_ip
		table.insert(addresses, hostname)
	else
		addresses = dnsutils.resolve(hostname)
		if #addresses == 0 then
			r:write("No DNS records found for " .. hostname)
			return apache2.OK
		end
	end

	local ok = false
	local tested_address
	local verified = false

	for _, address in ipairs(addresses) do
		tested_address = address

		if iputils.is_ipv6(address) then
			address = "[" .. address .. "]:" .. port
		else
			address = address .. ":" .. port
		end

		r:write(string.format("Attempting to connect to %s...\n", address))

		ok, verified = test_address(certificate, address, r)
		if ok then
			break
		end
	end

	if not ok then
		r:write("Connection failed, please make sure your server is publicly reachable.\n")
		return apache2.OK
	end

	if verified then
		r:write("Your certificate is validated by a CA, congratulations!\n")
	end

	local database, error = r:dbacquire("mod_dbd")
	if error then
		r:err("Failed to connect to SQL database: " .. error)
		return 500
	end

	local statement, error = database:prepare(r, "SELECT pw FROM servers WHERE name = %s")
	if error then
		r:err("Failed to prepare SQL query for password check: " .. error)
		database:close()
		return 500
	end

	local result, error = statement:select(name)
	if error then
		r:err("Failed to execute SQL query for password check: " .. error)
		database:close()
		return 500
	end

	local password_hash = hash(password)
	local row = result(-1)
	local updated = false

	if row and row[1] then
		if password_hash ~= row[1] then
			r:write("Invalid password for already registered server!\n")
			r.status = 401
			database:close()
			return apache2.OK
		end

		updated = true
	end


	statement, error = database:prepare(r, "REPLACE INTO servers (name, pw, ip, port, geoip, url, digest, verify) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)")
	if error then
		r:err("Failed to prepare SQL query for registration: " .. error)
 		database:close()
 		return 500
	end

	result, error = statement:query(name, password_hash, hostname, port, tested_address, url, digest, (verified and "1" or "0"))
	if error then
		r:err("Failed to execute SQL query for registration: " .. error)
		database:close()
		return 500
	end

	r:write(string.format("Registration %s!\n", updated and "updated" or "completed"))

	musage.store(database, 0, r, server)

	database:close()
	return apache2.OK
end
