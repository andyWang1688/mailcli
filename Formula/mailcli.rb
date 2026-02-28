class Mailcli < Formula
  include Language::Python::Virtualenv

  desc "Mail CLI for IMAP/SMTP workflows"
  homepage "https://github.com/andyWang1688/mailcli"
  url "https://github.com/andyWang1688/mailcli/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_RELEASE_TARBALL_SHA256"
  license "MIT"

  depends_on "python@3.13"

  resource "click" do
    url "https://files.pythonhosted.org/packages/00/00/click-8.3.0.tar.gz"
    sha256 "9b9f285302c6e3064f4330c05f05b81945b2a39544279343e6e7c5f27a9baddc"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Mail CLI", shell_output("#{bin}/mailcli --help")
  end
end
