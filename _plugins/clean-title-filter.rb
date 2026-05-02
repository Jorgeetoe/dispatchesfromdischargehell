module Jekyll
  module CleanTitleFilter
    def clean_seo_title(input)
      return input if input.nil?

      # Remove series numbering prefixes for SEO titles
      # Matches: "Post 1:", "Post 2:", "Part 1:", "Part 5", etc.
      input.gsub(/^(?:Post|Part)\s+\d+:\s*/, '').strip
    end
  end
end

Liquid::Template.register_filter(Jekyll::CleanTitleFilter)
