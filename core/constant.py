from django.db import models
from django.utils.translation import gettext_lazy as _


class DisasterIdentifier(models.TextChoices):
    I101 = '101', _("Banjir")
    I102 = '102', _("Tanah Longsor")
    # I103 = '103', _("....")
    I104 = '104', _("Abrasi")
    I105 = '105', _("Puting Beliung")
    I106 = '106', _("Kekeringan")
    I107 = '107', _("Kebakaran Hutan dan Lahan")
    I108 = '108', _("Gempa Bumi")
    I109 = '109', _("Tsunami")
    I110 = '110', _("Gempa Bumi dan Tsunami")
    I111 = '111', _("Letusan Gunung Api")
    I999 = '999', _("Lainnya")


class VictimAgeGroup(models.TextChoices):
    AG101 = '101', _("Bayi")
    AG102 = '102', _("Balita")
    AG103 = '103', _("Anak-anak")
    AG104 = '104', _("Remaja")
    AG105 = '105', _("Dewasa")
    AG106 = '106', _("Lansia")
    AG107 = '107', _("Ibu Hamil")
    AG999 = '999', _("Tidak diketahui")


class VictimGender(models.TextChoices):
    G101 = '101', _("Laki-laki")
    G102 = '102', _("Perempuan")
    G999 = '999', _("Tidak diketahui")


class VictimClassify(models.TextChoices):
    C101 = '101', _("Meninggal")
    C102 = '102', _("Hilang")
    C103 = '103', _("Terluka")
    C104 = '104', _("Menderita")
    C105 = '105', _("Mengungsi")
    C999 = '999', _("Tidak diketahui")


class DamageClassify(models.TextChoices):
    C101 = '101', _("Bangunan")
    C102 = '102', _("Lahan")
    C103 = '103', _("Ekonomi")
    C999 = '999', _("Lainnya")


class DamageVariety(models.TextChoices):
    V101 = '101', _("Rumah")
    V102 = '102', _("Pendidikan")
    V103 = '103', _("Peribadatan")
    V104 = '104', _("Kesehatan")
    V105 = '105', _("Perkantoran")
    V106 = '106', _("Fasilitas Umum")
    V107 = '107', _("Jembatan")
    V108 = '108', _("Pabrik")
    V109 = '109', _("Pertokoan")
    V110 = '110', _("Sawah (ha)")
    V111 = '111', _("Kebun (ha)")
    V112 = '112', _("Perkebunan (ha)")
    V113 = '113', _("Lahan (ha)")
    V114 = '114', _("Hutan (ha)")
    V115 = '115', _("Kolam (ha)")
    V116 = '116', _("Irigasi (km)")
    V117 = '117', _("Jalan (km)")
    V118 = '118', _("Kerugian (jt Rp.)")
    V999 = '999', _("Lainnya")


class DamageLevel(models.TextChoices):
    L101 = '101', _("Ringan")
    L102 = '102', _("Sedang")
    L103 = '103', _("Berat")
    L999 = '999', _("Lainnya")


class DamageMetric(models.TextChoices):
    M101 = '101', _("Hektare")
    M102 = '102', _("Unit")
    M103 = '103', _("Kilometer")
    M104 = '104', _("Rupiah")
    M999 = '999', _("Lainnya")


class ConfirmationReaction(models.TextChoices):
    CR101 = '101', _("True")
    CR102 = '102', _("False")


class ReactionIdentifier(models.TextChoices):
    RI101 = '101', _("Like")
    RI102 = '102', _("Celebrate")
    RI103 = '103', _("Support")
    RI104 = '104', _("Love")
    RI105 = '105', _("Insightful")
    RI106 = '106', _("Curious")
