-- Copyright 2021 The Mumble Developers. All rights reserved.
-- Use of this source code is governed by a BSD-style license
-- that can be found in the LICENSE file at the root of the
-- Mumble source tree or at <https://www.mumble.info/LICENSE>.

local ffi = require "cffi"
local unbound = require "lunbound"

local AF_INET = 2
local AF_INET6 = 10

local INET_ADDRSTRLEN = 16
local INET6_ADDRSTRLEN = 46

local RR_CLASS_IN = 1

local RR_TYPE_A = 1
local RR_TYPE_AAAA = 28

ffi.cdef[[
struct in_addr {
	unsigned long addr;
};

struct in6_addr {
	unsigned char addr[16];
};

typedef uint32_t socklen_t;
const char *inet_ntop(int af, const void *src, char *dst, socklen_t size);

size_t strnlen(const char *s, size_t maxlen);
]]

local dnsutils = {}

local ub_ctx = unbound.new({
	async = false;
	hoststxt = false;
	resolvconf = false;
})

function dnsutils.resolve(domain)
	local addresses = { }

	results = ub_ctx:resolve(domain, RR_TYPE_AAAA, RR_CLASS_IN)
	if not results then
		return {}
	end

	if results["havedata"] then
		local in6_addr = ffi.cast("struct in6_addr *", results[1])
		local buffer = ffi.new("char[?]", INET6_ADDRSTRLEN)
		ffi.C.inet_ntop(AF_INET6, in6_addr.addr, buffer, ffi.sizeof(buffer))
		local address = ffi.string(buffer, ffi.C.strnlen(buffer, ffi.sizeof(buffer)))
		table.insert(addresses, address)
	end

	results = ub_ctx:resolve(domain, RR_TYPE_A, RR_CLASS_IN)
	if results["havedata"] then
		local in_addr = ffi.cast("struct in_addr *", results[1])
		local buffer = ffi.new("char[?]", INET_ADDRSTRLEN)
		ffi.C.inet_ntop(AF_INET, ffi.addressof(in_addr.addr), buffer, ffi.sizeof(buffer))
		local address = ffi.string(buffer, ffi.C.strnlen(buffer, ffi.sizeof(buffer)))
		table.insert(addresses, address)
	end

	return addresses
end

return dnsutils
