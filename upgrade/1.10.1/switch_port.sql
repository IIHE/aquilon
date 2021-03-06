ALTER TABLE OBSERVED_MAC ADD PORT VARCHAR(32);

UPDATE OBSERVED_MAC SET PORT = TO_CHAR(PORT_NUMBER);

ALTER TABLE OBSERVED_MAC DROP CONSTRAINT "OBSERVED_MAC_PK";
ALTER TABLE OBSERVED_MAC DROP CONSTRAINT "OBSERVED_MAC_PORT_NUMBER_NN";
ALTER TABLE OBSERVED_MAC DROP COLUMN PORT_NUMBER;
ALTER TABLE OBSERVED_MAC DROP COLUMN SLOT;

ALTER TABLE OBSERVED_MAC ADD CONSTRAINT "OBSERVED_MAC_PK" PRIMARY KEY ("SWITCH_ID", "PORT", "MAC_ADDRESS") ENABLE;
ALTER TABLE OBSERVED_MAC MODIFY (PORT VARCHAR(32) CONSTRAINT "OBSERVED_MAC_PORT_NN" NOT NULL);
