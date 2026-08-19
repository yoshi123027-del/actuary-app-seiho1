const FILES = {
  "japanese-paper": "/admin-files/ICA2026_Japanese_refined_v5.pdf",
  "japanese-presentation": "/admin-files/0818%20%E6%97%A5%E6%9C%AC%E8%AA%9E%E7%89%88%E5%AE%8C%E6%88%90.pptx",
  "english-paper": "/admin-files/ICA2026_English_refined_v5.pdf",
};

export const dynamic = "force-dynamic";

export async function GET(request, { params }) {
  const { file } = await params;
  const target = FILES[file];

  if (!target) {
    return new Response("File not found", { status: 404 });
  }

  return Response.redirect(new URL(target, request.url), 307);
}
