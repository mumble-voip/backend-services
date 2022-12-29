DROP TABLE IF EXISTS public_servers;

CREATE TABLE public_servers (
	name,
	register_password,
	ip,
	port,
	website_url,
	certificate_hash,
	is_verified,
	PRIMARY KEY(ip, port)
)
