-- Migration 2.6 -> 2.7
--
-- Introduces the admin/host role split in `user_lobbys`:
--   owner=1 -> admin (lobby creator; at most one per lobby)
--   host=1  -> co-host (admin-promoted host)
--
-- The multi-host feature in commit ca34766 (2026-05-08) repurposed owner=1
-- to mean "any host", which broke account-deletion semantics: a co-host
-- deleting their account would cascade-delete the original creator's
-- lobbies. This migration restores the invariant that each lobby has at
-- most one owner=1 row, and demotes extra rows to host=1.

ALTER TABLE `user_lobbys` ADD COLUMN `host` BOOLEAN DEFAULT 0;

-- Backfill: for lobbies that picked up multiple owner=1 rows during the
-- multi-host window, keep the lowest user_id as admin and demote the rest
-- to host=1. user_lobbys has no timestamp, so MIN(user_id) is the best
-- available proxy for "earliest joined" (the creator is inserted first by
-- lobbys.create_lobby). For lobbies with a single owner=1, this is a no-op.
UPDATE `user_lobbys` ul
JOIN (
    SELECT lobby_id, MIN(user_id) AS keeper
    FROM `user_lobbys`
    WHERE owner = 1
    GROUP BY lobby_id
    HAVING COUNT(*) > 1
) keepers
    ON ul.lobby_id = keepers.lobby_id
   AND ul.user_id != keepers.keeper
SET ul.owner = 0,
    ul.host  = 1
WHERE ul.owner = 1;
