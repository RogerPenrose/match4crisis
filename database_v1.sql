-- Alle Eintraege und Tabellen auf einheitliche Sprache (Englisch) uebersetzen? :) --

CREATE TABLE "public.Users" (
	"id" serial,
	"Sprachen" TEXT NOT NULL,
	"Email" VARCHAR(255),
	"created_at" DATETIME,
	"PW_Hash" VARCHAR(255) NOT NULL,
	CONSTRAINT "Users_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);


-- ggf. verkuerzen? --
CREATE TABLE "public.Offer_Types" (
	"id" serial,
	"name" VARCHAR(255),
	"standard_view" VARCHAR(255) NOT NULL,
	CONSTRAINT "Offer_Types_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.Offers" (
	"offer_id" serial NOT NULL,
	"userid" integer NOT NULL,
	"TypeId" varchar(255) NOT NULL,
	"created_at" DATETIME NOT NULL,
	"updated_at" DATETIME NOT NULL,
	"digital" BOOLEAN NOT NULL,
--	"Weitere infos ----" VARCHAR(255) NOT NULL,
-- -> Nicht mehr noetig? ersetzt durch Tabellen wie "accomodation" etc.
	"aktiv" BOOLEAN NOT NULL,
	CONSTRAINT "Offers_pk" PRIMARY KEY ("offer_id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.Preferences" (
	"id" serial NOT NULL,
	"searches_accomodation" BOOLEAN NOT NULL,
	"searches_bureaucratic_aide" BOOLEAN NOT NULL,
-- 	"Ausbauen ja/nein?" VARCHAR(255) NOT NULL, -> Alles aus dem Registrationsformular
	CONSTRAINT "Preferences_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);

----------------------------------------------------------------------------------
--! Problem: PLZ kann nicht auf eine bestimmte Tabelle verweisen, wenn wir die !--
--! Tabellen in Accommodation, Food_Supply etc. unterteilen. -> im späteren    !--
--! Verlauf Loesungen suchen oder diese Tabelle wegfallen lassen. Ist nur ein  !--
--! Convenience-Tool                                                           !--
----------------------------------------------------------------------------------
-- CREATE TABLE "public.Lokalitäten" (
-- 	"PLZ" integer NOT NULL,
-- 	"ID_Angebot" integer NOT NULL,
-- 	CONSTRAINT "Lokalitäten_pk" PRIMARY KEY ("PLZ")
-- ) WITH (
--   OIDS=FALSE
-- );
-- Bei auskommentierung beachten: unten, alter table fuer die foreign-keys

-- Beispieltabelle zur einteilung in Offer-Types --
CREATE TABLE "public.Accomodation" (
	"offer_id" integer NOT NULL,
	"Land" VARCHAR(255) NOT NULL,
	"PLZ" VARCHAR(255) NOT NULL,
	"#Bewohner" integer NOT NULL,
	"Haustiere" BOOLEAN NOT NULL,
	"Straße" VARCHAR(255) NOT NULL,
	"Nummer" VARCHAR(255) NOT NULL,
	"Stay_length" DATETIME NOT NULL,
	"Cost" DECIMAL NOT NULL,
	CONSTRAINT "Accomodation_pk" PRIMARY KEY ("offer_id")
) WITH (
  OIDS=FALSE
);





ALTER TABLE "Offers" ADD CONSTRAINT "Offers_fk0" FOREIGN KEY ("userid") REFERENCES "Users"("id");
ALTER TABLE "Offers" ADD CONSTRAINT "Offers_fk1" FOREIGN KEY ("TypeId") REFERENCES "Offer_Types"("id");

ALTER TABLE "Preferences" ADD CONSTRAINT "Preferences_fk0" FOREIGN KEY ("id") REFERENCES "Users"("id");

-- ALTER TABLE "Lokalitäten" ADD CONSTRAINT "Lokalitäten_fk0" FOREIGN KEY ("PLZ") REFERENCES "Accommodation"("PLZ");
-- Nicht zwangsweise accomodation, sondern die jeweilgie Tabelle
-- ALTER TABLE "Lokalitäten" ADD CONSTRAINT "Lokalitäten_fk1" FOREIGN KEY ("ID_Angebot") REFERENCES "Offers"("offer_id");

ALTER TABLE "Accomodation" ADD CONSTRAINT "Accomodation_fk0" FOREIGN KEY ("offer_id") REFERENCES "Offers"("offer_id");
