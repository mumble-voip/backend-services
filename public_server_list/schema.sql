DROP TABLE IF EXISTS public_servers;

CREATE TABLE public_servers (
	name UNIQUE,
	register_password,
	ip,
	port,
	website_url,
	certificate_hash,
	is_verified,
	last_active DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(ip, port)
)
