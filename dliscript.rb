require 'rubygems'
require 'mechanize'
require 'logger'

$domainRoot = "http://www.new1.dli.ernet.in"
$baseUrl = "http://www.new1.dli.ernet.in/cgi-bin/advsearch_db.cgi?listStart=%d&language1=Urdu&perPage=%d"

rootDir = ARGV[0]

Dir.mkdir(rootDir) if not File.directory?(rootDir)
Dir.chdir(rootDir)

$logger = Logger.new('dliscript.rb.log')

class String
  def starts_with?(prefix)
    prefix = prefix.to_s
    self[0, prefix.length] == prefix
  end
end

class BookItem
  attr_accessor :subject
  attr_accessor :year
  attr_accessor :bar_code
  attr_accessor :pages
  attr_accessor :title
  attr_accessor :metadata_link
  attr_accessor :content_link
  attr_accessor :first_page
  attr_accessor :last_page
  attr_accessor :content_path
  
  def initialize(subject=nil, year=nil, bar_code=nil, pages=nil, title=nil, metadata_link=nil)
    @subject = subject
    @year = year
    @bar_code = bar_code
    @pages = pages
    @title = title
    @metadata_link = metadata_link
  end
  
end


def parseLink(link)
  book = BookItem.new  
  tokens = link.split('&')
  tokens.each { |token|
    parts = token.split('=')
    
    book.subject = parts[1].to_s.strip if parts[0] == 'subject1'
    book.year = parts[1].to_s.strip if parts[0] == 'year'
    book.bar_code = parts[1].to_s.strip if parts[0] == 'barcode'
    book.pages = parts[1].to_s.strip.to_i if parts[0] == 'pages'
    book.title = parts[1].to_s.strip if parts[0] == 'title1'
    book.content_path = parts[1].to_s.strip if parts[0] == 'url'
  }

  book.first_page = 1
  book.last_page = book.pages
  book.metadata_link = link
  
  return book  
end

def get_page_name(page)
  page.to_s.rjust(8, '0')
end

def get_page_name_with_extension(page)
  get_page_name(page) + '.tif'
end

def get_page_url(book, page)
  $domainRoot + book.content_path + '/PTIFF/' + get_page_name_with_extension(page)
end

def get_group_dir_name(start, ending)
  start.to_s + '-' + ending.to_s
end

def save_book(book, file)
  file.puts "Title=#{book.title}"
  file.puts "Barcode=#{book.bar_code}"
  file.puts "Pages=#{book.pages.to_s}"
  file.puts "Subject=#{book.subject}"
  file.puts "Year=#{book.year}"
  file.puts "Content-Path=#{book.content_path}"
  file.puts "First-Page=#{book.first_page}"
  file.puts "Last-Page=#{book.last_page}"
  file.puts "Metadata-Link=#{book.metadata_link}"
end

mechanize = Mechanize.new { |agent|
  agent.user_agent_alias = 'Mac Safari'
  agent.log = $logger
}

(0..2000).step(20).each { |index|
  group_dir_name = get_group_dir_name(index, index + 20)
  Dir.mkdir(group_dir_name) if not File.directory?(group_dir_name)
  Dir.chdir(group_dir_name)
  
  items_list_page = mechanize.get($baseUrl % [index, 20])
  books = []
  items_list_page.links.each { |link|
    book = parseLink(link.href) if link.href.starts_with?('metainfo.cgi')
    books.push(book)
  }    
  
  books.each { |book|
    Dir.mkdir book.bar_code if not File.directory? book.bar_code
    Dir.chdir(book.bar_code)
    
    File.open('.meta', 'w+') { |file| save_book(book, file) }
    
    (book.first_page .. book.last_page).each { |page|
      page_url = get_page_url(book, page)
      begin
        $logger.info 'Downloading %s' % page_url
        if not File.exists?(get_page_name_with_extension(page))
          mechanize.get(page_url).save()
        else
          $logger.info 'Skipping download of already existing file %s' % get_page_name_with_extension(page)
        end
      rescue
        $logger.error 'Failed to download %s' % page_url
      end
    }
  }
}
