seznam_html = """{% extends 'rezervace/base.html' %}

{% block content %}
<h1>Rezervační systém</h1>

<div class="rezervace_wizard">
    <div class="wizard_navigace">
        <ul>
            <li class="first wizard_act_step"><a class="wizard_act_step" href="{% url 'seznam_prostoru' %}"><b>1. krok<br><span>Zvolení služby</span></b></a></li>
            <li><b>2. krok<br><span>Výběr termínu</span></b></li>
            <li class="last"><b>3. krok<br><span>Vyplnění údajů</span></b></li>
        </ul>
    </div>
</div>

<div class="rezervace_step_inf">
    <p>V tomto kroku zvolte prostor, na který chcete učinit rezervaci. V následujících krocích zvolíte termín rezervace a zadáte kontaktní údaje. O stavu rezervace budete informováni e-mailem.</p>
</div>

<ul class="kalendare_list">
    {% for prostor in prostory %}
    <li class="kalendar">
        <a href="{% url 'vytvorit_rezervaci_krok1' %}?prostor={{ prostor.id }}">{{ prostor.nazev }}</a>
        <span class="popis">{{ prostor.popis|linebreaksbr }}</span>
        <span class="adresa">Návsí</span>
    </li>
    {% empty %}
    <li>Zatím nejsou k dispozici žádné prostory k rezervaci.</li>
    {% endfor %}
</ul>
{% endblock %}
"""

krok1_html = """{% extends 'rezervace/base.html' %}

{% block content %}
<style>
    .kalendar-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .kalendar-table th, .kalendar-table td { text-align: center; vertical-align: middle; padding: 5px; border: 1px solid #dee2e6; }
    .kalendar-table th { color: #154b2a; font-weight: bold; background: #f8f9fa; }
    .den-box { display: block; width: 100%; height: 40px; line-height: 40px; text-decoration: none; font-weight: bold; }
    .den-volno { background-color: #e6f2eb; color: #154b2a; }
    .den-volno:hover { background-color: #154b2a; color: white; }
    .den-obsazeno { background-color: #fff; color: #dc3545; }
    .den-vybrano { background-color: #154b2a; color: white; }
    .den-minulost { background-color: #f1f1f1; color: #adb5bd; }
    .kalendar-wrapper { max-width: 600px; margin-bottom: 30px; }
    .rez-cas-table { width: 100%; margin-top: 20px; border-collapse: collapse; }
    .rez-cas-table th, .rez-cas-table td { padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }
    .rez-cas-table th { background: #f4f4f4; }
    .btn-navsi { background-color: #154b2a; color: white; padding: 8px 15px; border: none; text-decoration: none; display: inline-block; cursor: pointer; font-weight: bold; }
    .btn-navsi:hover { background-color: #0e331c; color: white; }
</style>

<h1>Rezervační systém - {{ vybrany_prostor.nazev }}</h1>

<div class="rezervace_wizard">
    <div class="wizard_navigace">
        <ul>
            <li class="first"><a href="{% url 'seznam_prostoru' %}"><b>1. krok<br><span>Zvolení služby</span></b></a></li>
            <li class="wizard_act_step"><a class="wizard_act_step" href="#"><b>2. krok<br><span>Výběr termínu</span></b></a></li>
            <li class="last"><b>3. krok<br><span>Vyplnění údajů</span></b></li>
        </ul>
    </div>
</div>

<div class="rezervace_step_inf">
    <p>Vyberte v kalendáři požadované datum. Poté se Vám zobrazí volné časy, ze kterých si můžete vybrat.</p>
</div>

<div class="kalendar-wrapper">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <a href="?prostor={{ vybrany_prostor.id }}&rok={{ pred_r }}&mesic={{ pred_m }}" class="btn-navsi">&larr; Předchozí</a>
        <h3 style="margin: 0; color: #154b2a;">{{ nazev_mesice }} {{ zobrazovany_rok }}</h3>
        <a href="?prostor={{ vybrany_prostor.id }}&rok={{ dalsi_r }}&mesic={{ dalsi_m }}" class="btn-navsi">Další &rarr;</a>
    </div>

    <table class="kalendar-table">
        <thead>
            <tr><th>Po</th><th>Út</th><th>St</th><th>Čt</th><th>Pá</th><th>So</th><th>Ne</th></tr>
        </thead>
        <tbody>
            {% for tyden in kalendar_data %}
            <tr>
                {% for den in tyden %}
                <td>
                    {% if den.stav == 'prazdny' %}
                    {% elif den.stav == 'minulost' or den.stav == 'obsazeno' %}
                        <div class="den-box den-{{ den.stav }}">{{ den.den }}</div>
                    {% else %}
                        <a href="?prostor={{ vybrany_prostor.id }}&datum={{ den.datum }}&rok={{ zobrazovany_rok }}&mesic={{ zobrazovany_mesic }}" 
                           class="den-box den-{{ den.stav }}">{{ den.den }}</a>
                    {% endif %}
                </td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

{% if vybrane_datum %}
<h3 style="color: #154b2a; border-bottom: 1px solid #154b2a; padding-bottom: 5px;">Dostupné časy ({{ vybrane_datum }})</h3>
<form method="POST">
    {% csrf_token %}
    <input type="hidden" name="prostor" value="{{ vybrany_prostor.id }}">
    <input type="hidden" name="datum" value="{{ vybrane_datum }}">

    <table class="rez-cas-table">
        <thead>
            <tr>
                <th>Čas od - do</th>
                <th>Stav</th>
                <th style="text-align: right;">Akce</th>
            </tr>
        </thead>
        <tbody>
            {% for slot in sloty %}
            <tr>
                <td style="font-weight: bold;">{{ slot.cas_od }} - {{ slot.cas_do }}</td>
                <td>
                    {% if slot.obsazeno %}
                        <span style="color: #dc3545; font-weight: bold;">Obsazeno</span>
                    {% else %}
                        <span style="color: #154b2a; font-weight: bold;">Volno</span>
                    {% endif %}
                </td>
                <td style="text-align: right;">
                    {% if slot.obsazeno %}
                        <span style="color: #999;">Nedostupné</span>
                    {% else %}
                        <button type="submit" name="vybrany_cas" value="{{ slot.hodnota }}" class="btn-navsi">
                            Rezervovat
                        </button>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</form>
{% endif %}

<div style="margin-top: 30px;">
    <a href="{% url 'seznam_prostoru' %}" style="color: #666;">&larr; Zpět na výběr služby</a>
</div>
{% endblock %}
"""

krok2_html = """{% extends 'rezervace/base.html' %}

{% block content %}
<style>
    .form-navsi { max-width: 600px; margin-top: 20px; }
    .form-navsi label { display: block; font-weight: bold; margin-bottom: 5px; color: #333; }
    .form-navsi input[type="text"], 
    .form-navsi input[type="email"], 
    .form-navsi input[type="password"],
    .form-navsi select,
    .form-navsi textarea {
        width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; font-family: inherit;
    }
    .form-navsi input[type="checkbox"] { margin-right: 10px; }
    .btn-navsi { background-color: #154b2a; color: white; padding: 10px 20px; border: none; cursor: pointer; font-weight: bold; font-size: 1.1em; width: 100%; }
    .btn-navsi:hover { background-color: #0e331c; }
    .form-navsi .helptext { display: block; font-size: 0.85em; color: #666; margin-top: -10px; margin-bottom: 15px; }
    .form-navsi .error { color: #dc3545; font-size: 0.9em; margin-top: -10px; margin-bottom: 10px; display: block; }
</style>

<h1>Rezervační systém - Dokončení</h1>

<div class="rezervace_wizard">
    <div class="wizard_navigace">
        <ul>
            <li class="first"><a href="{% url 'seznam_prostoru' %}"><b>1. krok<br><span>Zvolení služby</span></b></a></li>
            <li><a href="javascript:history.back()"><b>2. krok<br><span>Výběr termínu</span></b></a></li>
            <li class="last wizard_act_step"><a class="wizard_act_step" href="#"><b>3. krok<br><span>Vyplnění údajů</span></b></a></li>
        </ul>
    </div>
</div>

<div class="rezervace_step_inf">
    <p>Vyplňte prosím své kontaktní údaje. Po odeslání obdržíte potvrzení na Váš e-mail.</p>
</div>

<div class="form-navsi">
    <form method="POST">
        {% csrf_token %}
        
        {% for field in form %}
            <div>
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {{ field }}
                {% if field.help_text %}
                    <span class="helptext">{{ field.help_text }}</span>
                {% endif %}
                {% if field.errors %}
                    <span class="error">{{ field.errors.0 }}</span>
                {% endif %}
            </div>
        {% endfor %}
        
        <div style="margin-top: 20px;">
            <button type="submit" class="btn-navsi">
                Potvrdit a odeslat rezervaci
            </button>
        </div>
    </form>
</div>

<div style="margin-top: 30px;">
    <a href="javascript:history.back()" style="color: #666;">&larr; Zpět na výběr termínu</a>
</div>
{% endblock %}
"""

import os
base_dir = "rezervace/templates/rezervace"
with open(os.path.join(base_dir, "seznam_prostoru.html"), "w", encoding="utf-8") as f:
    f.write(seznam_html)
with open(os.path.join(base_dir, "krok1.html"), "w", encoding="utf-8") as f:
    f.write(krok1_html)
with open(os.path.join(base_dir, "krok2.html"), "w", encoding="utf-8") as f:
    f.write(krok2_html)

print("Templates updated.")
