"""
HIPPOCRATES Agent - Scientific Reviewer for CyraSoul.

This agent reviews content for health & wellness accuracy,
validates claims against scientific literature, and ensures
medical responsibility.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


@dataclass
class HealthClaim:
    """A health claim found in content."""
    claim: str
    location: str  # Where in the content
    severity: str  # low, medium, high risk
    verified: bool
    source: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ScientificReview:
    """Result of scientific review."""
    is_approved: bool
    overall_score: float  # 0-100
    claims_found: List[HealthClaim]
    issues: List[str]
    suggestions: List[str]
    citations_added: List[str]
    revised_content: Optional[str] = None


class HippocratesAgent:
    """
    HIPPOCRATES - Scientific Reviewer.

    Reviews wellness content for accuracy, validates health claims,
    and ensures medical responsibility.
    """

    SYSTEM_PROMPT = """Sen sağlık ve wellness içerik doğrulama uzmanısın. Adın HIPPOCRATES.

## Görevin
- Tüm sağlık iddialarını bilimsel literatürle doğrula
- Desteklenmeyen veya yanıltıcı iddiaları işaretle
- Güncel araştırmalara referans ekle
- İçeriğin tıbbi olarak sorumlu olduğundan emin ol

## Değerlendirme Kriterleri

### Sağlık İddiaları
1. **Düşük Risk**: Genel wellness tavsiyeleri (su içmek, uyku düzeni)
2. **Orta Risk**: Supplement faydaları, diyet önerileri
3. **Yüksek Risk**: Hastalık tedavisi, tıbbi müdahale iddiaları

### Yasak İfadeler
- "Kesinlikle işe yarar"
- "Garantili sonuç"
- "Tüm hastalıkları tedavi eder"
- "Doktor onaylı" (doğrulanmadıkça)
- "Mucizevi etki"
- "Yan etkisi yok"

### Önerilen İfadeler
- "Araştırmalar gösteriyor ki..."
- "Birçok kullanıcı ... bildirmiştir"
- "... desteklemeye yardımcı olabilir"
- "Düzenli kullanımda ... katkıda bulunabilir"
- "Bir sağlık uzmanına danışmanızı öneririz"

## Çıktı Formatı
```json
{
  "is_approved": true/false,
  "overall_score": 0-100,
  "claims": [
    {
      "claim": "İddia metni",
      "location": "Bölüm/paragraf",
      "severity": "low/medium/high",
      "verified": true/false,
      "source": "Kaynak (varsa)",
      "suggestion": "Düzeltme önerisi (gerekirse)"
    }
  ],
  "issues": ["Sorun 1", "Sorun 2"],
  "suggestions": ["Öneri 1", "Öneri 2"],
  "citations_added": ["Eklenen kaynak 1"],
  "revised_content": "Düzeltilmiş içerik (gerekirse)"
}
```"""

    def __init__(
        self,
        model: str = "claude-opus-4-5-20250514",
        max_tokens: int = 4096
    ):
        """
        Initialize HIPPOCRATES agent.

        Args:
            model: Claude model to use (Opus for better accuracy).
            max_tokens: Maximum tokens in response.
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def review_content(
        self,
        content: str,
        title: str,
        scientific_context: Optional[str] = None
    ) -> ScientificReview:
        """
        Review content for scientific accuracy.

        Args:
            content: Content to review.
            title: Content title.
            scientific_context: RAG-retrieved scientific context.

        Returns:
            ScientificReview with findings and suggestions.
        """
        user_message = self._build_review_message(content, title, scientific_context)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        response_text = response.content[0].text
        return self._parse_review_response(response_text)

    def _build_review_message(
        self,
        content: str,
        title: str,
        scientific_context: Optional[str]
    ) -> str:
        """Build the review request message."""
        parts = []

        parts.append(f"## İncelenecek İçerik")
        parts.append(f"**Başlık:** {title}")
        parts.append(f"\n{content}")

        if scientific_context:
            parts.append("\n## Bilimsel Referanslar")
            parts.append(scientific_context)

        parts.append("\n## Görev")
        parts.append("""Bu içeriği bilimsel doğruluk açısından incele:
1. Tüm sağlık iddialarını tespit et
2. Her iddiayı risk seviyesine göre değerlendir
3. Desteklenmeyen iddiaları işaretle
4. Gerekli düzeltmeleri öner
5. Eksik uyarıları belirt
6. Genel değerlendirme puanı ver

Çıktını belirtilen JSON formatında ver.""")

        return "\n".join(parts)

    def _parse_review_response(self, response_text: str) -> ScientificReview:
        """Parse the review response into ScientificReview."""
        import json
        import re

        # Try to extract JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)

        if json_match:
            try:
                data = json.loads(json_match.group(1))

                # Parse claims
                claims = []
                for claim_data in data.get("claims", []):
                    claims.append(HealthClaim(
                        claim=claim_data.get("claim", ""),
                        location=claim_data.get("location", ""),
                        severity=claim_data.get("severity", "low"),
                        verified=claim_data.get("verified", False),
                        source=claim_data.get("source"),
                        suggestion=claim_data.get("suggestion")
                    ))

                return ScientificReview(
                    is_approved=data.get("is_approved", False),
                    overall_score=float(data.get("overall_score", 0)),
                    claims_found=claims,
                    issues=data.get("issues", []),
                    suggestions=data.get("suggestions", []),
                    citations_added=data.get("citations_added", []),
                    revised_content=data.get("revised_content")
                )

            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        # Fallback: Create basic review from text
        return ScientificReview(
            is_approved=False,
            overall_score=50.0,
            claims_found=[],
            issues=["İnceleme sonucu JSON formatında ayrıştırılamadı"],
            suggestions=["İçeriği manuel olarak gözden geçirin"],
            citations_added=[],
            revised_content=None
        )

    def verify_claim(
        self,
        claim: str,
        context: Optional[str] = None
    ) -> HealthClaim:
        """
        Verify a specific health claim.

        Args:
            claim: The health claim to verify.
            context: Additional context for verification.

        Returns:
            HealthClaim with verification result.
        """
        user_message = f"""## Doğrulanacak İddia
{claim}

{"## Bağlam" + chr(10) + context if context else ""}

## Görev
Bu sağlık iddiasını değerlendir:
1. Risk seviyesini belirle (low/medium/high)
2. Bilimsel literatürle doğrula
3. Kaynak var mı kontrol et
4. Düzeltme önerisi sun

JSON formatında yanıtla:
```json
{{
  "claim": "iddia",
  "severity": "low/medium/high",
  "verified": true/false,
  "source": "kaynak (varsa)",
  "suggestion": "öneri"
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
                return HealthClaim(
                    claim=data.get("claim", claim),
                    location="",
                    severity=data.get("severity", "medium"),
                    verified=data.get("verified", False),
                    source=data.get("source"),
                    suggestion=data.get("suggestion")
                )
            except json.JSONDecodeError:
                pass

        return HealthClaim(
            claim=claim,
            location="",
            severity="medium",
            verified=False,
            suggestion="Manuel doğrulama gerekli"
        )

    def add_disclaimers(self, content: str) -> str:
        """
        Add necessary health disclaimers to content.

        Args:
            content: Original content.

        Returns:
            Content with added disclaimers.
        """
        user_message = f"""## İçerik
{content}

## Görev
Bu içeriğe gerekli sağlık uyarılarını ekle:
1. Tıbbi tavsiye yerine geçmediğini belirt
2. Sağlık uzmanına danışma önerisini ekle
3. Bireysel sonuçların değişebileceğini belirt

Uyarıları doğal bir şekilde içeriğe entegre et.
Sadece güncellenmiş içeriği döndür."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        return response.content[0].text
