BEGIN;
ALTER TABLE peer_peeringpoint RENAME management_ip TO router_id;
END;