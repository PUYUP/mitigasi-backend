from django.db import models
from django.utils.translation import gettext_lazy as _


class DisasterIdentifier(models.TextChoices):
    DIS101 = '101', _("Banjir")
    DIS102 = '102', _("Tanah Longsor")
    # DIS103 = '103', _("....")
    DIS104 = '104', _("Abrasi")
    DIS105 = '105', _("Puting Beliung")
    DIS106 = '106', _("Kekeringan")
    DIS107 = '107', _("Kebakaran Hutan dan Lahan")
    DIS108 = '108', _("Gempa Bumi")
    DIS109 = '109', _("Tsunami")
    DIS110 = '110', _("Gempa Bumi dan Tsunami")
    DIS111 = '111', _("Letusan Gunung Api")
    DIS999 = '999', _("Lainnya")


class HazardClassify(models.TextChoices):
    HAC101 = '101', _("Banjir")
    HAC102 = '102', _("Badai")
    HAC103 = '103', _("Tanah Longsor")
    HAC104 = '104', _("Kebakaran")
    HAC105 = '105', _("Gempa Bumi")
    HAC106 = '106', _("Abrasi")
    HAC107 = '107', _("Kekeringan")
    HAC108 = '108', _("Tsunami")
    HAC109 = '109', _("Letusan Gunung")
    HAC999 = '999', _("Lainnya")


class VictimAgeGroup(models.TextChoices):
    VAG101 = '101', _("Bayi")
    VAG102 = '102', _("Balita")
    VAG103 = '103', _("Anak-anak")
    VAG104 = '104', _("Remaja")
    VAG105 = '105', _("Dewasa")
    VAG106 = '106', _("Lansia")
    VAG107 = '107', _("Ibu Hamil")
    VAG999 = '999', _("Tidak diketahui")


class VictimGender(models.TextChoices):
    VIG101 = '101', _("Laki-laki")
    VIG102 = '102', _("Perempuan")
    VIG999 = '999', _("Tidak diketahui")


class VictimClassify(models.TextChoices):
    VIC101 = '101', _("Meninggal")
    VIC102 = '102', _("Hilang")
    VIC103 = '103', _("Terluka")
    VIC104 = '104', _("Menderita")
    VIC105 = '105', _("Mengungsi")
    VIC999 = '999', _("Tidak diketahui")


class DamageClassify(models.TextChoices):
    DAC101 = '101', _("Bangunan")
    DAC102 = '102', _("Lahan")
    DAC103 = '103', _("Ekonomi")
    DAC999 = '999', _("Lainnya")


class DamageVariety(models.TextChoices):
    DAV101 = '101', _("Rumah")
    DAV102 = '102', _("Pendidikan")
    DAV103 = '103', _("Peribadatan")
    DAV104 = '104', _("Kesehatan")
    DAV105 = '105', _("Perkantoran")
    DAV106 = '106', _("Fasilitas Umum")
    DAV107 = '107', _("Jembatan")
    DAV108 = '108', _("Pabrik")
    DAV109 = '109', _("Pertokoan")
    DAV110 = '110', _("Sawah (ha)")
    DAV111 = '111', _("Kebun (ha)")
    DAV112 = '112', _("Perkebunan (ha)")
    DAV113 = '113', _("Lahan (ha)")
    DAV114 = '114', _("Hutan (ha)")
    DAV115 = '115', _("Kolam (ha)")
    DAV116 = '116', _("Irigasi (km)")
    DAV117 = '117', _("Jalan (km)")
    DAV118 = '118', _("Kerugian (jt Rp.)")
    DAV999 = '999', _("Lainnya")


class DamageLevel(models.TextChoices):
    DAL101 = '101', _("Ringan")
    DAL102 = '102', _("Sedang")
    DAL103 = '103', _("Berat")
    DAL999 = '999', _("Lainnya")


class DamageMetric(models.TextChoices):
    DAM101 = '101', _("Hektare")
    DAM102 = '102', _("Unit")
    DAM103 = '103', _("Kilometer")
    DAM104 = '104', _("Rupiah")
    DAM999 = '999', _("Lainnya")


class ConfirmationReaction(models.TextChoices):
    COR101 = '101', _("True")
    COR102 = '102', _("False")


class ReactionIdentifier(models.TextChoices):
    REI101 = '101', _("Like")
    REI102 = '102', _("Celebrate")
    REI103 = '103', _("Support")
    REI104 = '104', _("Love")
    REI105 = '105', _("Insightful")
    REI106 = '106', _("Curious")
