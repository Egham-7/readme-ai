import { Card, CardHeader, CardContent } from "@/components/ui/card";

const LoadingSkeleton = () => (
  <Card className="w-full max-w-4xl mx-auto">
    <CardHeader>
      <div className="h-6 w-48 bg-muted animate-pulse rounded" />
      <div className="h-4 w-full md:w-96 bg-muted animate-pulse rounded mt-2" />
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="flex justify-end">
        <div className="h-8 w-32 bg-muted animate-pulse rounded" />
      </div>
      <div className="space-y-4">
        <div className="h-8 w-48 bg-muted animate-pulse rounded" />
        <div className="h-96 w-full bg-muted animate-pulse rounded" />
      </div>
    </CardContent>
  </Card>
);

export default LoadingSkeleton;
