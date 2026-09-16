from django import template

register = template.Library()

# Classic HD icon pack portraits (static/images/client-icons/), used as a stable
# per-client "random" avatar in the client list — deterministic on the client's
# pk so the same client always gets the same portrait instead of reshuffling
# on every page load.
CLIENT_ICONS = [
    "Abomination.png",
    "Archer.png",
    "Archmage.png",
    "Banshee.png",
    "BlackDragon.png",
    "BloodMage.png",
    "BlueDragon.png",
    "CryptFiend.png",
    "CryptLord.png",
    "DarkRanger.png",
    "Destroyer.png",
    "DruidoftheClaw.png",
    "DruidoftheTalon.png",
    "Dryad.png",
    "FarSeer.png",
    "Footman.png",
    "Ghoul.png",
    "GrandTurtle.png",
    "GreenDragonSmall.png",
    "Grunt.png",
    "Huntress.png",
    "IllidanEvil.png",
    "Jaina.png",
    "Kenarius.png",
    "Knight.png",
    "LichKelThuzad.png",
    "Maiev.png",
    "Malfurion.png",
    "Mediv.png",
    "NagaMyrmidon.png",
    "NagaSeaWitch.png",
    "NagaSiren.png",
    "Peon.png",
    "PriestessoftheMoon.png",
    "RedDragon.png",
    "Rexxar.png",
    "Rifleman.png",
    "Roshan.png",
    "Shaman.png",
    "Sorceress.png",
    "SpellBreaker.png",
    "SpiritWalker.png",
    "Tauren.png",
    "Thrall.png",
    "TrollHeadhunter.png",
    "Varimatas.png",
    "archimond.png",
    "doomguard.png",
    "felguard.png",
    "golem.png",
    "pitlord.png",
]


@register.filter
def client_icon(client):
    """Static path to a portrait icon, stable per client (based on its pk)."""
    icon = CLIENT_ICONS[client.pk % len(CLIENT_ICONS)]
    return f"images/client-icons/{icon}"
