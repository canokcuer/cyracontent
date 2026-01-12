"""
NEO Agent - SEO Optimizer for CyraSoul.

This agent optimizes content for Turkish search queries,
improves meta tags, and ensures SEO best practices.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


@dataclass
class SEOMetadata:
    """SEO metadata for content."""
    title: str
    meta_description: str
    slug: str
    primary_keyword: str
    secondary_keywords: List[str]
    alt_texts: List[str]  # For images


@dataclass
class SEOAnalysis:
    """SEO analysis results."""
    score: float  # 0-100
    title_score: float
    meta_score: float
    heading_score: float
    keyword_score: float
    readability_score: float
    issues: List[str]
    suggestions: List[str]


@dataclass
class SEOOptimizedContent:
    """Content optimized for SEO."""
    content: str
    metadata: SEOMetadata
    analysis: SEOAnalysis
    internal_links: List[Dict[str, str]]  # {"text": "anchor", "url": "/path"}
    schema_markup: Optional[str] = None


class NeoAgent:
    """
    NEO - SEO Optimization Specialist.

    Optimizes Turkish wellness content for search engines,
    improves visibility and readability.
    """

    SYSTEM_PROMPT = """Sen SEO optimizasyon uzmanısın. Adın NEO.

## Görevin
- Türkçe arama sorgularına göre içeriği optimize et
- Meta başlık ve açıklamaları iyileştir
- Başlık hiyerarşisini düzenle
- Dahili link önerileri sun
- Anahtar kelime optimizasyonu yap

## SEO Kuralları

### Başlık (Title Tag)
- Maksimum 60 karakter
- Ana anahtar kelimeyi başta kullan
- Marka adını sonunda ekle (| CyraSoul)
- Dikkat çekici ve açıklayıcı ol

### Meta Açıklama
- 150-160 karakter arası
- Ana anahtar kelimeyi içer
- Eylem çağrısı ekle
- Değer önerisini belirt

### Başlık Hiyerarşisi
- Tek H1 (sayfa başlığı)
- H2'ler ana bölümler için
- H3'ler alt konular için
- Mantıklı sıralama

### Anahtar Kelime Kullanımı
- Ana anahtar kelime: %1-2 yoğunluk
- İlk 100 kelimede kullan
- H2 başlıklarında kullan
- Doğal akışı koru

### URL Slug
- Kısa ve açıklayıcı
- Türkçe karaktersiz (ı→i, ş→s, etc.)
- Tire ile kelime ayırma
- Ana anahtar kelimeyi içer

### İç Linkler
- İlgili blog yazılarına link
- Ürün sayfalarına doğal linkler
- Anchor text çeşitliliği

## CyraSoul İç Link Hedefleri
- /blog/ - Blog ana sayfası
- /products/dailyglow - DailyGlow ürün sayfası
- /products/dreamglow - DreamGlow ürün sayfası
- /products/mindfuel - MindFuel ürün sayfası
- /products/reset-button - Reset Button ürün sayfası
- /products/thechill - TheChill ürün sayfası
- /saglik-akademisi - Sağlık Akademisi
- /hakkimizda - Hakkımızda

## Çıktı Formatı
```json
{
  "optimized_content": "SEO optimize edilmiş içerik (markdown)",
  "metadata": {
    "title": "SEO Başlık | CyraSoul",
    "meta_description": "Meta açıklama...",
    "slug": "url-slug",
    "primary_keyword": "ana anahtar kelime",
    "secondary_keywords": ["ikincil", "kelimeler"],
    "alt_texts": ["görsel için alt metin"]
  },
  "analysis": {
    "score": 85,
    "title_score": 90,
    "meta_score": 85,
    "heading_score": 80,
    "keyword_score": 85,
    "readability_score": 88,
    "issues": ["Sorun varsa"],
    "suggestions": ["İyileştirme önerisi"]
  },
  "internal_links": [
    {"text": "anchor text", "url": "/hedef-sayfa"}
  ],
  "schema_markup": "JSON-LD schema (opsiyonel)"
}
```"""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096
    ):
        """
        Initialize NEO agent.

        Args:
            model: Claude model to use.
            max_tokens: Maximum tokens in response.
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def optimize_content(
        self,
        content: str,
        title: str,
        target_keywords: Optional[List[str]] = None,
        content_type: str = "blog"
    ) -> SEOOptimizedContent:
        """
        Optimize content for SEO.

        Args:
            content: Content to optimize.
            title: Current title.
            target_keywords: Target keywords to optimize for.
            content_type: Type of content (blog, product, etc.)

        Returns:
            SEOOptimizedContent with optimizations.
        """
        user_message = self._build_optimization_message(
            content, title, target_keywords, content_type
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        response_text = response.content[0].text
        return self._parse_optimization_response(response_text, content)

    def _build_optimization_message(
        self,
        content: str,
        title: str,
        target_keywords: Optional[List[str]],
        content_type: str
    ) -> str:
        """Build the optimization request message."""
        parts = []

        parts.append("## Optimize Edilecek İçerik")
        parts.append(f"**Mevcut Başlık:** {title}")
        parts.append(f"**İçerik Türü:** {content_type}")

        if target_keywords:
            parts.append(f"**Hedef Anahtar Kelimeler:** {', '.join(target_keywords)}")

        parts.append(f"\n### İçerik\n{content}")

        parts.append("\n## Görev")
        parts.append("""Bu içeriği SEO açısından optimize et:
1. Başlık ve meta açıklama oluştur
2. URL slug öner
3. Başlık hiyerarşisini düzenle
4. Anahtar kelime kullanımını optimize et
5. Dahili link fırsatlarını belirle
6. SEO puanı hesapla

Çıktını belirtilen JSON formatında ver.""")

        return "\n".join(parts)

    def _parse_optimization_response(
        self,
        response_text: str,
        original_content: str
    ) -> SEOOptimizedContent:
        """Parse the optimization response."""
        import json
        import re

        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)

        if json_match:
            try:
                data = json.loads(json_match.group(1))

                # Parse metadata
                meta_data = data.get("metadata", {})
                metadata = SEOMetadata(
                    title=meta_data.get("title", ""),
                    meta_description=meta_data.get("meta_description", ""),
                    slug=meta_data.get("slug", ""),
                    primary_keyword=meta_data.get("primary_keyword", ""),
                    secondary_keywords=meta_data.get("secondary_keywords", []),
                    alt_texts=meta_data.get("alt_texts", [])
                )

                # Parse analysis
                analysis_data = data.get("analysis", {})
                analysis = SEOAnalysis(
                    score=float(analysis_data.get("score", 0)),
                    title_score=float(analysis_data.get("title_score", 0)),
                    meta_score=float(analysis_data.get("meta_score", 0)),
                    heading_score=float(analysis_data.get("heading_score", 0)),
                    keyword_score=float(analysis_data.get("keyword_score", 0)),
                    readability_score=float(analysis_data.get("readability_score", 0)),
                    issues=analysis_data.get("issues", []),
                    suggestions=analysis_data.get("suggestions", [])
                )

                return SEOOptimizedContent(
                    content=data.get("optimized_content", original_content),
                    metadata=metadata,
                    analysis=analysis,
                    internal_links=data.get("internal_links", []),
                    schema_markup=data.get("schema_markup")
                )

            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        # Fallback
        return SEOOptimizedContent(
            content=original_content,
            metadata=SEOMetadata(
                title="",
                meta_description="",
                slug="",
                primary_keyword="",
                secondary_keywords=[],
                alt_texts=[]
            ),
            analysis=SEOAnalysis(
                score=0,
                title_score=0,
                meta_score=0,
                heading_score=0,
                keyword_score=0,
                readability_score=0,
                issues=["SEO analizi tamamlanamadı"],
                suggestions=["Manuel optimizasyon gerekli"]
            ),
            internal_links=[]
        )

    def analyze_seo(self, content: str, title: str) -> SEOAnalysis:
        """
        Analyze content for SEO without making changes.

        Args:
            content: Content to analyze.
            title: Content title.

        Returns:
            SEOAnalysis with scores and suggestions.
        """
        user_message = f"""## Analiz Edilecek İçerik
**Başlık:** {title}

{content}

## Görev
Bu içeriğin SEO performansını analiz et:
1. Başlık etkinliği
2. Meta açıklama (varsa)
3. Başlık hiyerarşisi
4. Anahtar kelime kullanımı
5. Okunabilirlik

Sadece analiz sonuçlarını JSON formatında ver:
```json
{{
  "score": 0-100,
  "title_score": 0-100,
  "meta_score": 0-100,
  "heading_score": 0-100,
  "keyword_score": 0-100,
  "readability_score": 0-100,
  "issues": ["sorunlar"],
  "suggestions": ["öneriler"]
}}
```"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        response_text = response.content[0].text

        import json
        import re

        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)

        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return SEOAnalysis(
                    score=float(data.get("score", 0)),
                    title_score=float(data.get("title_score", 0)),
                    meta_score=float(data.get("meta_score", 0)),
                    heading_score=float(data.get("heading_score", 0)),
                    keyword_score=float(data.get("keyword_score", 0)),
                    readability_score=float(data.get("readability_score", 0)),
                    issues=data.get("issues", []),
                    suggestions=data.get("suggestions", [])
                )
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        return SEOAnalysis(
            score=0,
            title_score=0,
            meta_score=0,
            heading_score=0,
            keyword_score=0,
            readability_score=0,
            issues=["Analiz başarısız"],
            suggestions=[]
        )

    def generate_schema_markup(
        self,
        content_type: str,
        title: str,
        description: str,
        **kwargs
    ) -> str:
        """
        Generate JSON-LD schema markup for content.

        Args:
            content_type: Type of content (Article, Product, etc.)
            title: Content title.
            description: Content description.
            **kwargs: Additional schema properties.

        Returns:
            JSON-LD schema markup string.
        """
        import json

        if content_type == "blog":
            schema = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": title,
                "description": description,
                "author": {
                    "@type": "Organization",
                    "name": "CyraSoul"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "CyraSoul",
                    "url": "https://cyrasoul.com"
                },
                **kwargs
            }
        elif content_type == "product":
            schema = {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": title,
                "description": description,
                "brand": {
                    "@type": "Brand",
                    "name": "CyraSoul"
                },
                **kwargs
            }
        else:
            schema = {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": title,
                "description": description,
                **kwargs
            }

        return json.dumps(schema, ensure_ascii=False, indent=2)

    def turkish_to_slug(self, text: str) -> str:
        """
        Convert Turkish text to URL-friendly slug.

        Args:
            text: Turkish text.

        Returns:
            URL-friendly slug.
        """
        import re

        # Turkish character mapping
        tr_map = {
            'ı': 'i', 'İ': 'i',
            'ğ': 'g', 'Ğ': 'g',
            'ü': 'u', 'Ü': 'u',
            'ş': 's', 'Ş': 's',
            'ö': 'o', 'Ö': 'o',
            'ç': 'c', 'Ç': 'c'
        }

        # Convert Turkish characters
        for tr_char, en_char in tr_map.items():
            text = text.replace(tr_char, en_char)

        # Lowercase
        text = text.lower()

        # Remove special characters, keep only alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s-]', '', text)

        # Replace spaces with hyphens
        text = re.sub(r'\s+', '-', text)

        # Remove multiple consecutive hyphens
        text = re.sub(r'-+', '-', text)

        # Remove leading/trailing hyphens
        text = text.strip('-')

        return text
