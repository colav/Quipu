"""Regenera los ejemplos de respuesta (<ResponseExample>) de api-reference consultando la API de desarrollo.

El título de cada bloque es el código HTTP que devolvió la API (`json 200`, `json 404`, `json 200 — Institución`),
así que los códigos documentados siempre son los reales. Las respuestas se recortan y se anonimizan según la
convención del README: personas como `0000000001`, instituciones como `example-institution-id` y grupos como
`COL0000001`.

Uso:
    python scripts/generate_examples.py            # reescribe las páginas
    python scripts/generate_examples.py --check    # solo informa qué páginas cambiarían (sale con 1 si hay alguna)
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import requests

BASE = os.environ.get("API_BASE", "https://api.dev.impactu.colav.co")
ROOT = Path(__file__).parent.parent / "api-reference"
FENCE = "`" * 3
TIMEOUT = 300

# Muestras reales con identificadores estables (ROR, Minciencias, Scienti, DANE). La salida se anonimiza.
SAMPLES = {
    "institution": "03bp5hc83",
    "faculty": "03bp5hc83_20",
    "department": "03bp5hc83_2_21620003_3154",
    "group": "COL0001262",
    "person": "0000652113",
    "state": "05",
    "city": "05001",
}
MISSING_OBJECT_ID = "000000000000000000000000"
EXAMPLE_EMAIL = "usuario@example.com"


@dataclass
class Case:
    path: str
    params: dict = field(default_factory=dict)
    variant: str = ""
    method: str = "GET"
    body: dict | None = None


@dataclass
class Page:
    cases: list[Case]
    # merge=True: solo se reemplazan los bloques con el mismo título; los demás (p. ej. respuestas que exigen
    # sesión) se escriben a mano y se conservan.
    merge: bool = False


def listing(path: str, **params) -> list[Case]:
    """Un listado paginado: dos resultados y un parámetro inválido."""
    return [Case(path, {"max": 2, **params}), Case(path, {"max": 0})]


def products(path: str) -> list[Case]:
    return [Case(path, {"max": 2}), Case(path, {"fields": "titles,abstract"})]


def filters(path: str) -> list[Case]:
    return [Case(path), Case(path, {"max": 0})]


def detail(path: str, missing: str) -> list[Case]:
    return [Case(path), Case(missing)]


def unauthenticated(method: str, path: str, variant: str = "") -> Page:
    return Page([Case(path, method=method, variant=variant)], merge=True)


AFFILIATION_VARIANTS = [
    ("institution", "Institución"),
    ("faculty", "Facultad"),
    ("department", "Departamento"),
    ("group", "Grupo"),
]
USER = f"/admin/users/{EXAMPLE_EMAIL}"
APIKEY = f"/users/{EXAMPLE_EMAIL}/apikey"

PAGES: dict[str, Page] = {
    # Search
    "search/persons": Page(listing("/search/person")),
    "search/works": Page(listing("/search/works")),
    "search/works-filters": Page(filters("/search/works/filters")),
    "search/affiliations": Page(listing("/search/affiliations/institution")),
    "search/affiliations-filters": Page(
        [
            Case("/search/affiliations/institution/filters", variant="Institución"),
            Case("/search/affiliations/group/filters", variant="Grupo"),
            Case("/search/affiliations/institution/filters", {"max": 0}),
        ]
    ),
    "search/sources": Page(listing("/search/sources")),
    "search/sources-filters": Page(filters("/search/sources/filters")),
    "search/patents": Page(listing("/search/patents")),
    "search/projects": Page(listing("/search/projects")),
    "search/geo": Page(
        [
            Case("/search/geo/city", {"max": 2}, variant="Ciudad"),
            Case("/search/geo/state", {"max": 2}, variant="Departamento"),
            Case("/search/geo/country"),
        ]
    ),
    # Affiliation
    "affiliation/get-affiliation": Page(
        [Case(f"/affiliation/{t}/{{{t}}}", variant=label) for t, label in AFFILIATION_VARIANTS]
        + [Case("/affiliation/institution/0000000000")]
    ),
    "affiliation/get-related-affiliations": Page(
        [Case(f"/affiliation/{t}/{{{t}}}/affiliations", variant=label) for t, label in AFFILIATION_VARIANTS]
    ),
    "affiliation/get-research-products": Page(products("/affiliation/institution/{institution}/research/products")),
    "affiliation/get-research-products-filters": Page(
        filters("/affiliation/institution/{institution}/research/products/filters")
    ),
    "affiliation/get-research-patents": Page(listing("/affiliation/institution/{institution}/research/patents")),
    "affiliation/get-research-projects": Page(listing("/affiliation/institution/{institution}/research/projects")),
    "affiliation/get-research-news": Page(listing("/affiliation/institution/{institution}/research/news")),
    # Person
    "person/get-person": Page(detail("/person/{person}", "/person/9999999999")),
    "person/get-research-products": Page(products("/person/{person}/research/products")),
    "person/get-research-products-filters": Page(filters("/person/{person}/research/products/filters")),
    "person/get-research-patents": Page(listing("/person/{patent_person}/research/patents")),
    "person/get-research-projects": Page(listing("/person/{person}/research/projects")),
    "person/get-research-news": Page(listing("/person/{person}/research/news")),
    # Source
    "source/get-source": Page(detail("/source/{source}", f"/source/{MISSING_OBJECT_ID}")),
    "source/get-products": Page(products("/source/{source}/products")),
    "source/get-products-filters": Page(filters("/source/{source}/products/filters")),
    # Work, patent, project
    "work/get-work": Page(detail("/work/{work}", f"/work/{MISSING_OBJECT_ID}") + [Case("/work/abc")]),
    "work/get-work-authors": Page(detail("/work/{work}/authors", f"/work/{MISSING_OBJECT_ID}/authors")),
    "work/get-work-by-doi": Page([Case("/work", {"doi": "{doi}"}), Case("/work")]),
    "patent/get-patent": Page(detail("/patent/{patent}", f"/patent/{MISSING_OBJECT_ID}")),
    "patent/get-patent-authors": Page(detail("/patent/{patent}/authors", f"/patent/{MISSING_OBJECT_ID}/authors")),
    "project/get-project": Page(detail("/project/{project}", f"/project/{MISSING_OBJECT_ID}")),
    "project/get-project-authors": Page(detail("/project/{project}/authors", f"/project/{MISSING_OBJECT_ID}/authors")),
    # Geo
    "geo/get-geo": Page(
        [
            Case("/geo/state/{state}", variant="Departamento"),
            Case("/geo/city/{city}", variant="Ciudad"),
            Case("/geo/city/99999"),
        ]
    ),
    "geo/get-geo-affiliations": Page(
        [
            Case("/geo/state/{state}/affiliations", variant="Departamento"),
            Case("/geo/city/{city}/affiliations", variant="Ciudad"),
        ]
    ),
    "geo/get-geo-products": Page(listing("/geo/city/{city}/research/products")),
    # APC (CSV)
    "apc/search": Page([Case("/apc/search", {"max": 2}), Case("/apc/search", {"page": 11})]),
    "apc/person": Page([Case("/apc/person/{person}")]),
    "apc/affiliation": Page([Case("/apc/affiliation/{institution}")]),
    # Sistema
    "system/ping": Page([Case("/ping")]),
    "system/get-info": Page([Case("/info")]),
    "system/get-quality": Page([Case("/info/quality")]),
    # Autenticación, usuarios y cargas: solo las respuestas que no necesitan sesión ni escriben en la base.
    "auth/login": Page(
        [
            Case("/login", method="POST", body={}),
            Case("/login", method="POST", body={"email": EXAMPLE_EMAIL, "password": "contraseña-incorrecta"}),
        ],
        merge=True,
    ),
    "auth/logout": unauthenticated("POST", "/logout"),
    "auth/me": unauthenticated("GET", "/me", "sin sesión"),
    "users/list-users": unauthenticated("GET", "/admin/users"),
    "users/create-user": unauthenticated("POST", USER),
    "users/deactivate-user": unauthenticated("DELETE", USER),
    "users/activate-user": unauthenticated("PATCH", f"{USER}/restore"),
    "users/reset-password": unauthenticated("PATCH", USER),
    "users/edit-user": unauthenticated("PUT", USER),
    "users/create-apikey": unauthenticated("POST", APIKEY),
    "users/update-apikey": unauthenticated("PATCH", APIKEY),
    "users/delete-apikey": unauthenticated("DELETE", APIKEY),
    "submit/staff": unauthenticated("POST", "/submit/staff"),
    "submit/ciarp": unauthenticated("POST", "/submit/ciarp"),
    "submit/scienti": unauthenticated("POST", "/submit/scienti"),
    "submit/project": unauthenticated("POST", "/submit/project"),
}


def get_json(path: str, **params) -> dict:
    response = requests.get(BASE + path, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def resolve_samples() -> dict[str, str]:
    """Productos, fuentes, patentes y proyectos cambian de id con cada ejecución del ETL: se toman de la API."""
    samples = dict(SAMPLES)
    # Sin keywords, los primeros resultados son registros de Minciencias sin DOI.
    works = get_json("/search/works", keywords="covid", max=10)["data"]
    work = next(work for work in works if work.get("doi"))
    samples["work"], samples["doi"] = work["id"], work["doi"]
    samples["source"] = get_json("/search/sources", max=1)["data"][0]["id"]
    patent = get_json("/search/patents", max=1)["data"][0]
    samples["patent"] = patent["id"]
    samples["patent_person"] = next(author["id"] for author in patent["authors"] if author.get("id"))
    samples["project"] = get_json("/search/projects", max=1)["data"][0]["id"]
    return samples


# --- Anonimización ---------------------------------------------------------------------------------------------

ROR_RE = re.compile(r"^0[a-z0-9]{8}(?=$|_)")
GROUP_RE = re.compile(r"^COL\d{7}$")
PERSON_PATH_RE = re.compile(r"/person/(\d{10})")
# Ids de productos de Scienti y Minciencias que llevan el id de la persona: 0001549400-45, ART-0000541486-191.
PRODUCT_PERSON_RE = re.compile(r"(?:^|[A-Z]+-)(\d{10})-\d")
FAKE_NAMES = [
    ("María", "Ejemplo García"),
    ("Juan", "Ejemplo Pérez"),
    ("Ana", "Ejemplo López"),
    ("Carlos", "Ejemplo Rodríguez"),
    ("Laura", "Ejemplo Martínez"),
    ("Andrés", "Ejemplo Gómez"),
]
FAKE_PERSON_IDS = {
    "orcid": "https://orcid.org/0000-0000-0000-{n:04d}",
    "scholar": "https://scholar.google.com/citations?user=EXAMPLEID{n:02d}",
    "openalex": "https://openalex.org/A{n:010d}",
    "researchgate": "https://www.researchgate.net/profile/Ejemplo-{n}",
    "linkedin": "https://www.linkedin.com/in/ejemplo-{n}",
}
AFFILIATION_NAMES = {
    "institution": "Universidad Ejemplo",
    "faculty": "Facultad Ejemplo",
    "department": "Departamento Ejemplo",
    "group": "Grupo de Investigación Ejemplo",
}
VOLATILE_KEYS = {"db_response_time_ms": 25}
BIBTEX_KEY_RE = re.compile(r"@(\w+)\{[^,\n]*,")
BIBTEX_AUTHOR_RE = re.compile(r"author\s*=\s*\{.*?\}(?=,?\s*\n|,?\s*\}?\s*$)")


def anonymize_bibtex(bibtex: str) -> str:
    """La clave de cita y el campo author llevan los apellidos de los autores."""
    bibtex = BIBTEX_KEY_RE.sub(r"@\1{ejemplo,", bibtex)
    return BIBTEX_AUTHOR_RE.sub("author={Ejemplo García, María}", bibtex)


class Anonymizer:
    def __init__(self) -> None:
        self.replacements: dict[str, str] = {}
        self.persons: dict[str, int] = {}
        self.affiliations: dict[str, int] = {}
        self.counters: dict[str, int] = {}

    def _replace(self, real: str | None, fake: str) -> None:
        # Las cadenas cortas ("UdeA", "CO") cambiarían texto que no es un nombre.
        if real and len(real) >= 6 and real != fake:
            self.replacements.setdefault(real, fake)

    def person_number(self, person_id: str) -> int:
        return self.persons.setdefault(person_id, len(self.persons) + 1)

    def person_id(self, person_id: str) -> str:
        fake = f"{self.person_number(person_id):010d}"
        self._replace(person_id, fake)
        return fake

    def affiliation_id(self, affiliation_id: str) -> str:
        if GROUP_RE.match(affiliation_id):
            fake = f"COL{self._affiliation_number(affiliation_id, 'group'):07d}"
            self._replace(affiliation_id, fake)
            return fake
        root = ROR_RE.match(affiliation_id).group(0)  # type: ignore[union-attr]
        n = self._affiliation_number(root, "institution")
        fake_root = "example-institution-id" + ("" if n == 1 else f"-{n}")
        self._replace(root, fake_root)
        return fake_root + affiliation_id[len(root) :]

    def _affiliation_number(self, key: str, kind: str) -> int:
        if key not in self.affiliations:
            self.counters[kind] = self.counters.get(kind, 0) + 1
            self.affiliations[key] = self.counters[kind]
        return self.affiliations[key]

    def seed(self, path: str) -> None:
        """Los ids de la URL también salen en `cursor` y en los mensajes de error."""
        for match in PERSON_PATH_RE.finditer(path):
            self.person_id(match.group(1))
        for segment in path.split("/"):
            if ROR_RE.match(segment) or GROUP_RE.match(segment):
                self.affiliation_id(segment)

    def collect(self, node):
        if isinstance(node, list):
            for item in node:
                self.collect(item)
        elif isinstance(node, dict):
            node_id = node.get("id", node.get("_id"))
            if "full_name" in node:
                self._person(node)
            elif isinstance(node_id, str) and (ROR_RE.match(node_id) or GROUP_RE.match(node_id)):
                self._affiliation(node)
            # Antes del recorte: un texto cortado a la mitad del campo author ya no coincidiría.
            for key, value in node.items():
                if key == "bibtex" and isinstance(value, str):
                    node[key] = anonymize_bibtex(value)
            for value in node.values():
                self.collect(value)
        elif isinstance(node, str):
            for match in PRODUCT_PERSON_RE.finditer(node):
                self.person_id(match.group(1))

    def _person(self, person: dict) -> None:
        real_id = person.get("id")
        if isinstance(real_id, str) and real_id:
            n = self.person_number(real_id)
            person["id"] = self.person_id(real_id)
        else:
            # Coautores externos sin id: cada uno es una persona distinta.
            n = self.person_number(f"sin-id-{id(person)}")
        first, last = FAKE_NAMES[(n - 1) % len(FAKE_NAMES)]
        self._replace(person.get("full_name"), f"{first} {last}")
        for alias in person.get("aliases") or []:
            self._replace(alias, f"{first} {last}".lower())
        person["full_name"] = f"{first} {last}"
        if person.get("first_names") is not None:
            person["first_names"] = [first]
        if person.get("last_names") is not None:
            person["last_names"] = last.split()
        if person.get("initials") is not None:
            person["initials"] = first[0]
        if person.get("aliases") is not None:
            person["aliases"] = [f"{first} {last}".lower()]
        for external_id in person.get("external_ids") or []:
            source = external_id.get("source")
            if source == "scienti":
                fake = person["id"]
            else:
                fake = FAKE_PERSON_IDS.get(source, "example-{source}-{n}").format(n=n, source=source)
            self._replace(str(external_id.get("id")), fake)
            external_id["id"] = fake

    def _affiliation(self, affiliation: dict) -> None:
        key = "id" if "id" in affiliation else "_id"
        real_id = affiliation[key]
        affiliation[key] = self.affiliation_id(real_id)
        kind = (
            "group" if GROUP_RE.match(real_id) else ["institution", "faculty", "department"][min(real_id.count("_"), 2)]
        )
        n = self.affiliations[real_id if kind == "group" else ROR_RE.match(real_id).group(0)]  # type: ignore[union-attr]
        fake_name = AFFILIATION_NAMES[kind] + ("" if n == 1 or kind != "institution" else f" {n}")
        if isinstance(affiliation.get("name"), str):
            self._replace(affiliation["name"], fake_name)
            affiliation["name"] = fake_name
        for name in affiliation.get("names") or []:
            if isinstance(name, dict) and name.get("name"):
                self._replace(name["name"], fake_name)
                name["name"] = fake_name
        if affiliation.get("abbreviations"):
            affiliation["abbreviations"] = ["UE"]
        for url in affiliation.get("external_urls") or []:
            if isinstance(url, dict) and url.get("url"):
                url["url"] = "https://www.example.edu.co"
        for external_id in affiliation.get("external_ids") or []:
            if isinstance(external_id, dict) and external_id.get("id") is not None:
                fake = f"example-{external_id.get('source')}-id"
                self._replace(str(external_id["id"]), fake)
                external_id["id"] = fake

    def apply(self, node):
        if isinstance(node, list):
            return [self.apply(item) for item in node]
        if isinstance(node, dict):
            return {key: VOLATILE_KEYS.get(key, self.apply(value)) for key, value in node.items()}
        if isinstance(node, str):
            for real in sorted(self.replacements, key=len, reverse=True):
                node = node.replace(real, self.replacements[real])
        return node

    def text(self, value: str) -> str:
        return self.apply(value)


def shrink(value, items: int = 1, text: int = 160):
    """Recorta listas y textos largos para que los ejemplos sean legibles. El listado principal (`data`) conserva
    dos resultados; las listas anidadas, uno."""
    if isinstance(value, dict) and isinstance(value.get("data"), list):
        return {
            key: [shrink(item) for item in item_list[:2]] if key == "data" else shrink(item_list)
            for key, item_list in value.items()
        }
    if isinstance(value, list):
        return [shrink(item, items, text) for item in value[:items]]
    if isinstance(value, dict):
        return {key: shrink(item, items, text) for key, item in value.items()}
    if isinstance(value, str) and len(value) > text:
        return value[:text] + "…"
    return value


UNORDERED_KEYS = {"external_ids", "external_urls"}


def is_filter_options(value: list) -> bool:
    return bool(value) and all(isinstance(item, dict) and "value" in item for item in value)


def filter_option_order(option: dict) -> tuple:
    count = option.get("count")
    return (-count if isinstance(count, (int, float)) else 0, str(option["value"]))


def sort_unordered(value):
    """Ordena las listas cuyo orden cambia entre llamadas, para que el ejemplo recortado no cambie sin que cambien
    los datos: `external_ids`/`external_urls` salen de un set y las opciones de filtros empatan en `count`."""
    if isinstance(value, list):
        items = [sort_unordered(item) for item in value]
        return sorted(items, key=filter_option_order) if is_filter_options(items) else items
    if isinstance(value, dict):
        return {
            key: (
                sorted(sort_unordered(item), key=lambda entry: json.dumps(entry, sort_keys=True))
                if key in UNORDERED_KEYS and isinstance(item, list)
                else sort_unordered(item)
            )
            for key, item in value.items()
        }
    return value


def to_json(value, indent: int = 0, width: int = 120) -> str:
    """JSON con los objetos y listas cortos en una sola línea, como en los ejemplos escritos a mano."""
    inline = json.dumps(value, ensure_ascii=False)
    if not isinstance(value, (dict, list)) or not value or indent + len(inline) <= width:
        return inline
    pad = " " * (indent + 2)
    if isinstance(value, dict):
        items = [
            f"{pad}{json.dumps(key, ensure_ascii=False)}: {to_json(item, indent + 2, width)}"
            for key, item in value.items()
        ]
        return "{\n" + ",\n".join(items) + "\n" + " " * indent + "}"
    items = [f"{pad}{to_json(item, indent + 2, width)}" for item in value]
    return "[\n" + ",\n".join(items) + "\n" + " " * indent + "]"


# --- Generación ----------------------------------------------------------------------------------------------


def render(case: Case, samples: dict[str, str]) -> tuple[str, str]:
    """Devuelve (título, bloque de código) de la respuesta real del caso."""
    path = case.path.format(**samples)
    params = {key: str(value).format(**samples) for key, value in case.params.items()}
    response = requests.request(case.method, BASE + path, params=params, json=case.body, timeout=TIMEOUT)
    # Un 5xx es una falla de la API, no algo que documentar.
    if response.status_code >= 500:
        raise RuntimeError(f"{case.method} {path} {params} respondió {response.status_code}")
    title = f"{response.status_code}" + (f" — {case.variant}" if case.variant else "")
    anonymizer = Anonymizer()
    anonymizer.seed(path)
    if "text/csv" in response.headers.get("Content-Type", ""):
        # El CSV no declara charset y requests lo leería como Latin-1.
        lines = response.content.decode("utf-8-sig").splitlines()[:3]
        return title, f"{FENCE}csv {title}\n{anonymizer.text(chr(10).join(lines))}\n{FENCE}"
    # Se recolecta sobre la respuesta completa: un id puede aparecer en un autor que el recorte deja fuera.
    data = sort_unordered(response.json())
    anonymizer.collect(data)
    data = anonymizer.apply(shrink(data))
    return title, f"{FENCE}json {title}\n{to_json(data)}\n{FENCE}"


EXAMPLE_RE = re.compile(r"<ResponseExample>\n(.*?)\n?</ResponseExample>", re.DOTALL)
BLOCK_RE = re.compile(rf"{FENCE}\w+ ([^\n]*)\n.*?\n{FENCE}", re.DOTALL)


def merge_blocks(current: str, generated: list[tuple[str, str]]) -> str:
    blocks = [(match.group(1).strip(), match.group(0)) for match in BLOCK_RE.finditer(current)]
    for title, block in generated:
        index = next((i for i, (existing, _) in enumerate(blocks) if existing == title), None)
        if index is None:
            blocks.append((title, block))
        else:
            blocks[index] = (title, block)
    return "\n\n".join(block for _, block in blocks)


def update_page(page_path: Path, page: Page, samples: dict[str, str]) -> bool:
    content = page_path.read_text(encoding="utf-8")
    generated = [render(case, samples) for case in page.cases]
    match = EXAMPLE_RE.search(content)
    if match is None:
        raise ValueError(f"{page_path} no tiene <ResponseExample>")
    blocks = merge_blocks(match.group(1), generated) if page.merge else "\n\n".join(block for _, block in generated)
    updated = content[: match.start()] + f"<ResponseExample>\n{blocks}\n</ResponseExample>" + content[match.end() :]
    if updated == content:
        return False
    if "--check" not in sys.argv:
        page_path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    only = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    samples = resolve_samples()
    changed = []
    for name, page in PAGES.items():
        if only and name not in only:
            continue
        if update_page(ROOT / f"{name}.mdx", page, samples):
            changed.append(name)
        print(f"{'cambió' if name in changed else 'igual '}  {name}")
    print(f"\n{len(changed)} página(s) con ejemplos distintos de la API.")
    if changed and "--check" in sys.argv:
        sys.exit(1)


if __name__ == "__main__":
    main()
