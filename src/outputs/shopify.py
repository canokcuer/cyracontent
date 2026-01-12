"""
Shopify output handler for CyraSoul content.
Publishes content to Shopify blog via Admin API.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import httpx
from dotenv import load_dotenv

from ..agents.can import ContentOutput

load_dotenv()


@dataclass
class ShopifyPublishResult:
    """Result of Shopify publish operation."""
    success: bool
    article_id: Optional[str] = None
    article_url: Optional[str] = None
    error: Optional[str] = None


class ShopifyExporter:
    """
    Exports content to Shopify blog via Admin API.
    """

    def __init__(
        self,
        store_url: Optional[str] = None,
        access_token: Optional[str] = None,
        blog_id: Optional[str] = None
    ):
        """
        Initialize Shopify exporter.

        Args:
            store_url: Shopify store URL (e.g., mystore.myshopify.com).
            access_token: Shopify Admin API access token.
            blog_id: ID of the blog to post to.
        """
        self.store_url = store_url or os.getenv("SHOPIFY_STORE_URL")
        self.access_token = access_token or os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.blog_id = blog_id or os.getenv("SHOPIFY_BLOG_ID")

        if not self.store_url or not self.access_token:
            raise ValueError(
                "SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN environment variables are required"
            )

        # Build API URL
        self.api_url = f"https://{self.store_url}/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }

    def publish_article(
        self,
        content_output: ContentOutput,
        blog_id: Optional[str] = None,
        published: bool = False,
        tags: Optional[list] = None
    ) -> ShopifyPublishResult:
        """
        Publish content as a Shopify blog article.

        Args:
            content_output: Content to publish.
            blog_id: Blog ID to publish to.
            published: Whether to publish immediately.
            tags: Optional tags for the article.

        Returns:
            ShopifyPublishResult with article details.
        """
        blog_id = blog_id or self.blog_id
        if not blog_id:
            return ShopifyPublishResult(
                success=False,
                error="No blog_id provided. Set SHOPIFY_BLOG_ID or pass blog_id parameter."
            )

        try:
            # Convert markdown to HTML
            html_content = self._markdown_to_html(content_output.content)

            # Build article data
            article_data = {
                "article": {
                    "title": content_output.title,
                    "author": "CyraSoul",
                    "body_html": html_content,
                    "handle": content_output.slug,
                    "published": published,
                    "summary_html": f"<p>{content_output.meta_description}</p>",
                    "tags": ",".join(tags) if tags else ",".join(content_output.keywords[:5])
                }
            }

            # Add metafields for SEO
            article_data["article"]["metafields"] = [
                {
                    "namespace": "seo",
                    "key": "description",
                    "value": content_output.meta_description,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "custom",
                    "key": "seo_score",
                    "value": str(content_output.seo_score),
                    "type": "number_decimal"
                }
            ]

            # Make API request
            url = f"{self.api_url}/blogs/{blog_id}/articles.json"

            with httpx.Client() as client:
                response = client.post(
                    url,
                    json=article_data,
                    headers=self.headers,
                    timeout=30.0
                )

            if response.status_code in [200, 201]:
                data = response.json()
                article = data.get("article", {})
                return ShopifyPublishResult(
                    success=True,
                    article_id=str(article.get("id")),
                    article_url=f"https://{self.store_url}/blogs/{blog_id}/{content_output.slug}"
                )
            else:
                return ShopifyPublishResult(
                    success=False,
                    error=f"API Error: {response.status_code} - {response.text}"
                )

        except Exception as e:
            return ShopifyPublishResult(
                success=False,
                error=str(e)
            )

    def update_product_description(
        self,
        product_id: str,
        content: str,
        meta_description: Optional[str] = None
    ) -> ShopifyPublishResult:
        """
        Update a product's description.

        Args:
            product_id: Shopify product ID.
            content: New product description (HTML).
            meta_description: Optional meta description.

        Returns:
            ShopifyPublishResult.
        """
        try:
            product_data = {
                "product": {
                    "id": product_id,
                    "body_html": content
                }
            }

            if meta_description:
                product_data["product"]["metafields_global_description_tag"] = meta_description

            url = f"{self.api_url}/products/{product_id}.json"

            with httpx.Client() as client:
                response = client.put(
                    url,
                    json=product_data,
                    headers=self.headers,
                    timeout=30.0
                )

            if response.status_code == 200:
                return ShopifyPublishResult(
                    success=True,
                    article_id=product_id
                )
            else:
                return ShopifyPublishResult(
                    success=False,
                    error=f"API Error: {response.status_code} - {response.text}"
                )

        except Exception as e:
            return ShopifyPublishResult(
                success=False,
                error=str(e)
            )

    def get_blogs(self) -> list:
        """
        Get list of blogs from the store.

        Returns:
            List of blog dictionaries.
        """
        try:
            url = f"{self.api_url}/blogs.json"

            with httpx.Client() as client:
                response = client.get(url, headers=self.headers, timeout=30.0)

            if response.status_code == 200:
                return response.json().get("blogs", [])
            return []

        except Exception:
            return []

    def _markdown_to_html(self, markdown_content: str) -> str:
        """
        Convert markdown to HTML.

        Simple conversion for common markdown patterns.
        For production, consider using a proper markdown library.
        """
        import re

        html = markdown_content

        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Lists
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>\n)+', r'<ul>\g<0></ul>', html)

        # Paragraphs
        paragraphs = html.split('\n\n')
        processed = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<'):
                p = f'<p>{p}</p>'
            processed.append(p)
        html = '\n\n'.join(processed)

        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        return html
