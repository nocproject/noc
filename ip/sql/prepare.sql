ALTER TABLE ip_ipv4block ADD prefix_cidr CIDR NOT NULL;
CREATE INDEX x_ip_ipv4block_prefix_cidr ON ip_ipv4block(prefix_cidr);
ALTER TABLE ip_ipv4blockaccess ADD prefix_cidr CIDR NOT NULL;

CREATE OR REPLACE
FUNCTION ip_ipv4_block_depth(INTEGER,CIDR,CIDR)
RETURNS INTEGER
AS $$
DECLARE
    vrf         ALIAS FOR $1;
    inner_block ALIAS FOR $2;
    outer_block ALIAS FOR $3;
    c   INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO   c
    FROM ip_ipv4block
    WHERE vrf_id=vrf AND prefix_cidr >> inner_block AND prefix_cidr << outer_block;

    RETURN c;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE
FUNCTION hostname(TEXT)
RETURNS TEXT
AS $$
SELECT SUBSTRING($1 from E'^[a-zA-Z0-9\\-]+');
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE
FUNCTION domainname(TEXT)
RETURNS TEXT
AS $$
SELECT SUBSTRING($1 from E'^[a-zA-Z0-9\\-]+\\.(.+)'); 
$$ LANGUAGE SQL IMMUTABLE;

CREATE VIEW v_ip_ipv4block_city
AS
SELECT id,prefix_cidr,description
FROM ip_ipv4block
WHERE masklen(prefix_cidr)=11 AND prefix_cidr<<'10.0.0.0/8'::cidr;

CREATE OR REPLACE
FUNCTION find_city_block()
RETURNS SETOF ip_ipv4block
AS $$
DECLARE
    r  RECORD;
    r1 RECORD;
BEGIN
    FOR r IN SELECT prefix_cidr
        FROM ip_ipv4block
        WHERE masklen(prefix_cidr)=11 AND prefix_cidr << '10.0.0.0/8'::cidr
            AND vrf_id=1
    LOOP
        FOR r1 IN SELECT *
            FROM ip_ipv4block
            WHERE masklen(prefix_cidr)=16 AND prefix_cidr << r.prefix_cidr
                AND vrf_id=1
        LOOP
            RETURN NEXT r1;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE
FUNCTION create_service_block(INET,INTEGER,VARCHAR)
RETURNS VOID
AS $$
DECLARE
    p_mask        ALIAS FOR $1;
    p_masklen     ALIAS FOR $2;
    p_description ALIAS FOR $3;
BEGIN
    INSERT INTO ip_ipv4block(prefix,description,vrf_id,lir_id,asn_id)
    SELECT set_masklen(r.prefix_cidr|p_mask::inet,p_masklen)::text,p_description,r.vrf_id,r.lir_id,r.asn_id
    FROM find_city_block() r;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE
FUNCTION f_trigger_ip_ipv4block()
RETURNS TRIGGER
AS $$
BEGIN
    NEW.prefix_cidr:=NEW.prefix;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER t_ip_ipv4block_modify
BEFORE INSERT OR UPDATE ON ip_ipv4block
FOR EACH ROW EXECUTE PROCEDURE f_trigger_ip_ipv4block();

CREATE OR REPLACE
FUNCTION f_trigger_ip_ipv4blockaccess()
RETURNS TRIGGER
AS $$
BEGIN
    NEW.prefix_cidr:=NEW.prefix;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER t_ip_ipv4blockaccess_modify
BEFORE INSERT OR UPDATE ON ip_ipv4blockaccess
FOR EACH ROW EXECUTE PROCEDURE f_trigger_ip_ipv4blockaccess();