import { Input } from "./ui/input";
import { Search } from "lucide-react";

interface SearchHeaderProps {
  title: string;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  placeholder?: string;
}

export const SearchHeader = ({
  title,
  searchTerm,
  setSearchTerm,
  placeholder = "Search...",
}: SearchHeaderProps) => (
  <header className="bg-card shadow-sm">
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold text-card-foreground">{title}</h1>
      <div className="mt-4 relative">
        <Input
          type="text"
          placeholder={placeholder}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
        <Search
          className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground"
          size={20}
        />
      </div>
    </div>
  </header>
);
