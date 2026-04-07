import type { Metadata } from "next";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  return { title: `#${slug}` };
}

export default async function TagDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-4">
      <h1 className="text-lg font-medium text-foreground">#{slug}</h1>
      <div className="py-12 text-center text-sm text-muted-foreground">
        데이터 연동 후 관련 기사가 표시됩니다.
      </div>
    </div>
  );
}
