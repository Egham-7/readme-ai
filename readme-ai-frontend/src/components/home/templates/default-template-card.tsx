import {
  Card,
  CardTitle,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { FileIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

const DefaultTemplateCard = ({ onSelect }: { onSelect: () => void }) => (
  <Card className="group hover:border-primary/50 transition-colors">
    <CardHeader>
      <CardTitle className="text-lg flex items-center gap-2">
        <FileIcon className="h-5 w-5" />
        Default Template
      </CardTitle>
    </CardHeader>
    <CardContent>
      <p className="text-sm text-muted-foreground">
        Start with a basic README structure
      </p>
    </CardContent>
    <CardFooter>
      <Button onClick={onSelect} className="w-full">
        Use Default
      </Button>
    </CardFooter>
  </Card>
);

export default DefaultTemplateCard;
