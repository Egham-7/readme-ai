import {
  Card,
  CardHeader,
  CardDescription,
  CardContent,
  CardTitle,
} from "@/components/ui/card";

import { Loader2 } from "lucide-react";

const LoadingState = () => (
  <Card className="w-full max-w-4xl mx-auto">
    <CardHeader>
      <CardTitle>Generating README</CardTitle>
      <CardDescription>
        Please wait while we process your GitHub repository
      </CardDescription>
    </CardHeader>
    <CardContent className="flex flex-col items-center justify-center space-y-4">
      <Loader2 className="w-12 h-12 animate-spin text-primary" />
      <p className="text-center text-muted-foreground">
        This may take a few moments. We're analyzing your repository and
        crafting a tailored README.
      </p>
      <div className="max-w-md text-sm text-muted-foreground">
        <h4 className="font-semibold mb-2">Did you know?</h4>
        <ul className="list-disc list-inside space-y-1">
          <li>
            A good README can significantly increase your project's visibility
            and adoption.
          </li>
          <li>
            Including badges in your README can provide quick insights about
            your project's status.
          </li>
          <li>
            Regular updates to your README help maintain user engagement and
            project relevance.
          </li>
        </ul>
      </div>
    </CardContent>
  </Card>
);

export default LoadingState;
