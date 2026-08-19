const FILES = {
  "japanese-paper": {
    id: "1CFQs366N7VsVIRC4yZtyjc33uC2xDeND",
    filename: "ICA2026_Japanese_refined_v5.pdf",
    contentType: "application/pdf",
  },
  "japanese-presentation": {
    id: "1w8GFarXMPh0IHCeF8DTmYtTwqGGBXqw6",
    filename: "0818 日本語版完成.pptx",
    contentType: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  },
  "english-paper": {
    id: "1V47cxZImeJ40DJYz6n-pSfMuC-PSnQ1R",
    filename: "ICA2026_English_refined_v5.pdf",
    contentType: "application/pdf",
  },
};

export const dynamic = "force-dynamic";

export async function GET(_request, { params }) {
  const { file } = await params;
  const target = FILES[file];

  if (!target) {
    return new Response("File not found", { status: 404 });
  }

  const sourceUrl = `https://drive.usercontent.google.com/download?id=${encodeURIComponent(target.id)}&export=download&confirm=t`;

  try {
    const upstream = await fetch(sourceUrl, {
      redirect: "follow",
      cache: "no-store",
    });

    if (!upstream.ok || !upstream.body) {
      return new Response("Download source is unavailable", { status: 502 });
    }

    const encodedName = encodeURIComponent(target.filename);
    return new Response(upstream.body, {
      status: 200,
      headers: {
        "Content-Type": target.contentType,
        "Content-Disposition": `attachment; filename*=UTF-8''${encodedName}`,
        "Cache-Control": "private, no-store, max-age=0",
        "X-Content-Type-Options": "nosniff",
      },
    });
  } catch {
    return new Response("Download failed", { status: 502 });
  }
}
